"""Esquemas para el flujo de importación avanzada de CSV."""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class BankFormat(str, Enum):
    """Formatos soportados para detectar cabeceras y estilos de banco."""

    GENERIC = "generic"
    CAIXA = "caixa"
    SANTANDER = "santander"
    BBVA = "bbva"
    ING = "ing"


class ColumnMapping(BaseModel):
    """Mapeo entre columnas originales y roles funcionales."""

    fecha_col: str
    concepto_col: str
    importe_col: Optional[str] = None
    debe_col: Optional[str] = None
    haber_col: Optional[str] = None
    saldo_col: Optional[str] = None
    notas_col: Optional[str] = None


class ImportOptions(BaseModel):
    """Opciones configurables por el usuario durante la importación."""

    default_tipo_id: Optional[int] = Field(
        default=None,
        description="Tipo a aplicar si no se deduce del signo (1 gasto, 2 ingreso).",
    )
    default_categoria_id: Optional[int] = Field(
        default=None, description="Categoría a aplicar si no se obtiene de reglas."
    )
    default_metodo_pago_id: Optional[int] = Field(
        default=None, description="Método de pago por defecto."
    )
    detectar_tipo_por_signo: bool = Field(
        default=True, description="Usar el signo del importe para deducir gasto/ingreso."
    )
    aplicar_reglas: bool = Field(
        default=True, description="Ejecutar reglas de autocategorización al previsualizar."
    )
    ignorar_duplicados: bool = Field(
        default=True, description="Saltar filas que ya existan en la base de datos."
    )
    limpiar_concepto: bool = Field(
        default=True, description="Normalizar espacios en el concepto antes de validar."
    )
    formato_fecha: Optional[str] = Field(
        default=None, description="Formato de fecha esperado (por ejemplo %d/%m/%Y)."
    )


class CsvAnalysisResult(BaseModel):
    """Respuesta del análisis inicial del CSV subido."""

    format: BankFormat
    columns: list[str]
    sample: list[dict[str, Any]]
    suggested_mapping: Optional[ColumnMapping] = None
    warnings: list[str] = Field(default_factory=list)
    separator: Optional[str] = None


class CsvPreviewRow(BaseModel):
    """Fila enriquecida para mostrar en la previsualización."""

    raw_index: int
    fecha: Optional[date]
    concepto: str
    importe: Optional[float]
    saldo: Optional[float]
    tipo_id: Optional[int]
    categoria_id: Optional[int]
    metodo_pago_id: Optional[int]
    notas: Optional[str] = None
    is_duplicate: bool = False
    errors: list[str] = Field(default_factory=list)


class CsvPreviewResult(BaseModel):
    """Resultado agregado para la previsualización."""

    rows: list[CsvPreviewRow]
    total_rows: int
    valid_rows: int
    duplicate_rows: int
    error_rows: int
    summary_warnings: list[str] = Field(default_factory=list)


class CsvImportResult(BaseModel):
    """Resumen final de la importación definitiva."""

    imported: int
    skipped_duplicates: int
    skipped_errors: int
    total_rows: int
    examples_errors: list[CsvPreviewRow] = Field(default_factory=list)

