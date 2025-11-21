"""Servicio de importación avanzada desde CSV con previsualización.

Este módulo encapsula la detección de formatos bancarios, el análisis
preliminar del fichero, la previsualización y la importación efectiva de
movimientos, manteniendo la API limpia y extensible.
"""

from __future__ import annotations

import csv
import io
from datetime import date, datetime
from typing import Iterable, Optional, Tuple

import pandas as pd
from sqlalchemy.orm import Session

from backend.app.models import Movimiento
from backend.app.schemas.importacion import (
    BankFormat,
    ColumnMapping,
    CsvAnalysisResult,
    CsvImportResult,
    CsvPreviewResult,
    CsvPreviewRow,
    ImportOptions,
)
from backend.app.services.reglas import aplicar_reglas_movimiento

# Columnas típicas por formato para ayudar a la detección automática.
BANK_PROFILE_COLUMNS: dict[BankFormat, tuple[str, ...]] = {
    BankFormat.CAIXA: ("fecha operacion", "concepto", "importe", "saldo"),
    BankFormat.SANTANDER: ("fecha valor", "concepto", "importe"),
    BankFormat.BBVA: ("fecha", "descripcion", "importe", "saldo"),
    BankFormat.ING: ("fecha", "concepto", "importe", "saldo"),
    BankFormat.GENERIC: ("fecha", "concepto", "importe"),
}

# Patrones de fecha habituales por formato para sugerir parsing.
BANK_DATE_FORMATS: dict[BankFormat, tuple[str, ...]] = {
    BankFormat.CAIXA: ("%d/%m/%Y",),
    BankFormat.SANTANDER: ("%d/%m/%Y", "%Y-%m-%d"),
    BankFormat.BBVA: ("%d/%m/%Y",),
    BankFormat.ING: ("%Y-%m-%d", "%d/%m/%Y"),
    BankFormat.GENERIC: ("%Y-%m-%d", "%d/%m/%Y"),
}


def detectar_formato_banco(df: pd.DataFrame) -> BankFormat:
    """Devuelve el formato de banco más probable basándose en las cabeceras."""

    columnas = [col.strip().lower() for col in df.columns]
    puntuaciones: dict[BankFormat, int] = {}
    for formato, esperadas in BANK_PROFILE_COLUMNS.items():
        coincidencias = sum(1 for col in columnas for esp in esperadas if esp in col)
        puntuaciones[formato] = coincidencias
    if not puntuaciones:
        return BankFormat.GENERIC
    mejor_formato = max(puntuaciones.items(), key=lambda x: x[1])[0]
    return mejor_formato or BankFormat.GENERIC


def _detect_separator(sample: str) -> str:
    """Detecta el separador probable usando csv.Sniffer."""

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        return dialect.delimiter
    except Exception:  # noqa: BLE001
        return ","


def _read_csv_bytes(file_bytes: bytes) -> Tuple[pd.DataFrame, str]:
    """Lee el CSV intentando codificaciones comunes y detectando separador."""

    last_error: Optional[Exception] = None
    for encoding in ("utf-8", "latin-1"):
        try:
            sample = file_bytes[:1024].decode(encoding, errors="ignore")
            sep = _detect_separator(sample)
            buffer = io.StringIO(file_bytes.decode(encoding))
            df = pd.read_csv(buffer, sep=sep, engine="python")
            return df, sep
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            continue
    raise ValueError(f"No se pudo leer el CSV: {last_error}")


def _suggest_mapping(columns: Iterable[str]) -> Optional[ColumnMapping]:
    """Sugiere un mapeo de columnas basado en heurísticas simples."""

    cols = [c.lower() for c in columns]
    if not cols:
        return None
    mapping = ColumnMapping(fecha_col=cols[0], concepto_col=cols[0])
    fecha = next((c for c in cols if "fecha" in c), None)
    concepto = next((c for c in cols if "concepto" in c or "descr" in c), None)
    importe = next((c for c in cols if "importe" in c or "amount" in c), None)
    debe = next((c for c in cols if "debe" in c or "cargo" in c), None)
    haber = next((c for c in cols if "haber" in c or "abono" in c), None)
    saldo = next((c for c in cols if "saldo" in c or "balance" in c), None)
    notas = next((c for c in cols if "notas" in c or "detalle" in c), None)

    if fecha:
        mapping.fecha_col = fecha
    if concepto:
        mapping.concepto_col = concepto
    if importe:
        mapping.importe_col = importe
    if debe:
        mapping.debe_col = debe
    if haber:
        mapping.haber_col = haber
    if saldo:
        mapping.saldo_col = saldo
    if notas:
        mapping.notas_col = notas
    return mapping


def analyze_csv(file_bytes: bytes) -> CsvAnalysisResult:
    """Analiza el CSV detectando cabeceras, formato bancario y mapeo sugerido."""

    df, separator = _read_csv_bytes(file_bytes)
    formato = detectar_formato_banco(df)
    sample = df.head(5).fillna("").to_dict(orient="records")
    suggested_mapping = _suggest_mapping(df.columns)
    return CsvAnalysisResult(
        format=formato,
        columns=list(df.columns),
        sample=sample,
        suggested_mapping=suggested_mapping,
        warnings=[],
        separator=separator,
    )


def _parse_float(value) -> Optional[float]:
    """Convierte cadenas con coma o punto decimal a float."""

    if pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    texto = str(value).strip()
    if not texto:
        return None
    # Reemplazamos separadores europeos.
    texto = texto.replace(".", "").replace(",", ".") if "," in texto and texto.count(",") == 1 else texto
    try:
        return float(texto)
    except ValueError:
        return None


def _parse_date(value, override_format: Optional[str], candidatos: tuple[str, ...]) -> Optional[date]:
    """Parsea la fecha usando formatos sugeridos o el override indicado."""

    if pd.isna(value):
        return None
    if isinstance(value, date):
        return value
    texto = str(value).strip()
    if not texto:
        return None
    formatos = [override_format] if override_format else []
    formatos.extend([f for f in candidatos if f not in formatos])
    for fmt in formatos:
        try:
            return datetime.strptime(texto, fmt).date()
        except Exception:  # noqa: BLE001
            continue
    try:
        return pd.to_datetime(texto, dayfirst=True, errors="coerce").date()
    except Exception:  # noqa: BLE001
        return None


def _normalize_concept(value: str, limpiar: bool) -> str:
    """Normaliza un concepto para detección de duplicados y consistencia."""

    texto = value or ""
    if limpiar:
        texto = " ".join(texto.split())
    return texto.strip()


def _buscar_duplicado(
    db: Session, fecha: Optional[date], concepto_norm: str, importe: Optional[float]
) -> bool:
    """Comprueba si ya existe un movimiento con misma fecha, concepto e importe."""

    if fecha is None or importe is None:
        return False
    candidatos = (
        db.query(Movimiento)
        .filter(Movimiento.fecha == fecha, Movimiento.importe == importe)
        .all()
    )
    return any(_normalize_concept(m.concepto, True).lower() == concepto_norm for m in candidatos)


def _build_preview_rows(
    df: pd.DataFrame,
    mapping: ColumnMapping,
    options: ImportOptions,
    formato: BankFormat,
    db: Session,
) -> CsvPreviewResult:
    """Genera filas de previsualización aplicando normalizaciones y validaciones."""

    rows: list[CsvPreviewRow] = []
    error_rows = 0
    duplicate_rows = 0
    formatos_candidatos = BANK_DATE_FORMATS.get(formato, ("%Y-%m-%d",))
    vistos: set[tuple[Optional[date], str, Optional[float]]] = set()

    for idx, raw in df.iterrows():
        errores: list[str] = []
        fecha = _parse_date(raw.get(mapping.fecha_col), options.formato_fecha, formatos_candidatos)
        concepto_raw = str(raw.get(mapping.concepto_col, ""))
        concepto = _normalize_concept(concepto_raw, options.limpiar_concepto)

        importe = None
        if mapping.importe_col:
            importe = _parse_float(raw.get(mapping.importe_col))
        else:
            debe = _parse_float(raw.get(mapping.debe_col)) if mapping.debe_col else None
            haber = _parse_float(raw.get(mapping.haber_col)) if mapping.haber_col else None
            if debe is not None or haber is not None:
                importe = (haber or 0) - (debe or 0)

        saldo = _parse_float(raw.get(mapping.saldo_col)) if mapping.saldo_col else None
        notas = str(raw.get(mapping.notas_col, "")).strip() if mapping.notas_col else None

        if fecha is None:
            errores.append("Fecha inválida")
        if importe is None:
            errores.append("Importe inválido")
        tipo_id = None
        if options.detectar_tipo_por_signo and importe is not None:
            tipo_id = 1 if importe < 0 else 2
        elif options.default_tipo_id is not None:
            tipo_id = options.default_tipo_id

        categoria_id = options.default_categoria_id
        metodo_pago_id = options.default_metodo_pago_id

        # Aplicamos reglas de categorización si se solicita y no hay errores críticos.
        if options.aplicar_reglas and not errores and fecha and importe is not None:
            mock = Movimiento(
                fecha=fecha,
                concepto=concepto,
                importe=importe,
                saldo=saldo,
                notas=notas,
                tipo_id=tipo_id or options.default_tipo_id or 1,
                categoria_id=categoria_id or (options.default_categoria_id or 1),
                metodo_pago_id=metodo_pago_id or (options.default_metodo_pago_id or 1),
                anio=fecha.year,
                mes=fecha.month,
                mes_anio=f"{fecha.year:04d}-{fecha.month:02d}",
            )
            aplicar_reglas_movimiento(db, mock)
            categoria_id = mock.categoria_id

        concepto_norm = concepto.lower()
        ya_visto = (fecha, concepto_norm, importe) in vistos
        duplicado_bd = _buscar_duplicado(db, fecha, concepto_norm, importe)
        is_duplicate = ya_visto or duplicado_bd
        if is_duplicate:
            duplicate_rows += 1
        if ya_visto is False:
            vistos.add((fecha, concepto_norm, importe))

        if errores:
            error_rows += 1

        rows.append(
            CsvPreviewRow(
                raw_index=int(idx),
                fecha=fecha,
                concepto=concepto,
                importe=importe,
                saldo=saldo,
                tipo_id=tipo_id,
                categoria_id=categoria_id,
                metodo_pago_id=metodo_pago_id,
                notas=notas,
                is_duplicate=is_duplicate,
                errors=errores,
            )
        )

    valid_rows = len([r for r in rows if not r.errors])
    return CsvPreviewResult(
        rows=rows,
        total_rows=len(rows),
        valid_rows=valid_rows,
        duplicate_rows=duplicate_rows,
        error_rows=error_rows,
        summary_warnings=[],
    )


def preview_import(
    file_bytes: bytes, mapping: ColumnMapping, options: ImportOptions, db: Session
) -> CsvPreviewResult:
    """Relee el CSV aplicando el mapeo y devuelve una previsualización segura."""

    df, _ = _read_csv_bytes(file_bytes)
    return _build_preview_rows(df, mapping, options, detectar_formato_banco(df), db)


def apply_import(
    file_bytes: bytes,
    mapping: ColumnMapping,
    options: ImportOptions,
    db: Session,
    user_id: Optional[int] = None,
) -> CsvImportResult:
    """Importa definitivamente los movimientos válidos y no duplicados."""

    preview = preview_import(file_bytes, mapping, options, db)
    importables = [r for r in preview.rows if not r.errors]
    imported = 0
    skipped_dups = 0
    skipped_errors = preview.error_rows

    with db.begin():
        for row in importables:
            if row.is_duplicate and options.ignorar_duplicados:
                skipped_dups += 1
                continue

            movimiento = Movimiento(
                fecha=row.fecha,  # type: ignore[arg-type]
                concepto=row.concepto,
                importe=row.importe,  # type: ignore[arg-type]
                saldo=row.saldo,
                tipo_id=row.tipo_id
                or (options.default_tipo_id or (1 if (row.importe or 0) < 0 else 2)),
                categoria_id=row.categoria_id or (options.default_categoria_id or 1),
                metodo_pago_id=row.metodo_pago_id or (options.default_metodo_pago_id or 1),
                notas=row.notas,
            )
            movimiento.rellenar_campos_derivados()
            if options.aplicar_reglas:
                aplicar_reglas_movimiento(db, movimiento)
            db.add(movimiento)
            imported += 1

    ejemplos_error = [r for r in preview.rows if r.errors][:5]
    return CsvImportResult(
        imported=imported,
        skipped_duplicates=skipped_dups,
        skipped_errors=skipped_errors,
        total_rows=preview.total_rows,
        examples_errors=ejemplos_error,
    )

