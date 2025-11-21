"""Importación de movimientos desde CSV usando Pandas."""

from __future__ import annotations

from typing import Any

import pandas as pd
from fastapi import UploadFile
from sqlalchemy.orm import Session

from backend.app.models import Movimiento
from backend.app.schemas.movimientos import MovimientoCreate
from backend.app.services.movimientos import crear_movimiento

COLUMNAS_REQUERIDAS = {
    "fecha",
    "concepto",
    "importe",
    "saldo",
    "tipo_id",
    "categoria_id",
    "metodo_pago_id",
    "notas",
}


def procesar_csv(archivo: UploadFile, db: Session) -> dict[str, Any]:
    """Lee el CSV, valida columnas y crea movimientos."""

    df = pd.read_csv(archivo.file)
    columnas = set(df.columns.str.strip().str.lower())
    if not COLUMNAS_REQUERIDAS.issubset(columnas):
        faltantes = COLUMNAS_REQUERIDAS - columnas
        raise ValueError(f"Columnas requeridas ausentes: {', '.join(sorted(faltantes))}")

    df.columns = df.columns.str.strip().str.lower()
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce").dt.date

    insertados = 0
    errores: list[str] = []
    for idx, fila in df.iterrows():
        try:
            if pd.isna(fila["fecha"]):
                raise ValueError("Fecha inválida")
            datos = MovimientoCreate(
                fecha=fila["fecha"],
                concepto=str(fila["concepto"]),
                importe=float(fila["importe"]),
                saldo=None if pd.isna(fila.get("saldo")) else float(fila["saldo"]),
                tipo_id=int(fila["tipo_id"]),
                categoria_id=int(fila["categoria_id"]),
                metodo_pago_id=int(fila["metodo_pago_id"]),
                notas=None if pd.isna(fila.get("notas")) else str(fila["notas"]),
            )
            crear_movimiento(db, datos)
            insertados += 1
        except Exception as exc:  # noqa: BLE001
            errores.append(f"Fila {idx}: {exc}")
            db.rollback()
    return {"insertados": insertados, "errores": errores}
