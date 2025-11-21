"""Endpoints para análisis, previsualización e importación de CSV."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.importacion import (
    ColumnMapping,
    CsvAnalysisResult,
    CsvImportResult,
    CsvPreviewResult,
    ImportOptions,
)
from backend.app.services.importador_csv import analyze_csv, apply_import, preview_import

router = APIRouter(prefix="/import", tags=["importacion"])


@router.post("/analyze", response_model=CsvAnalysisResult)
async def analizar_csv(
    file: UploadFile = File(..., description="Fichero CSV a analizar"),
):
    """Analiza rápidamente el fichero para guiar al usuario en el mapeo."""

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo debe ser CSV")
    contenido = await file.read()
    return analyze_csv(contenido)


def _parse_payload(payload: str) -> tuple[ColumnMapping, ImportOptions]:
    """Parses mapping y options enviados como JSON en multipart."""

    try:
        data = json.loads(payload)
        mapping = ColumnMapping.model_validate(data.get("mapping"))
        options = ImportOptions.model_validate(data.get("options", {}))
        return mapping, options
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payload inválido: {exc}",
        ) from exc


@router.post("/preview", response_model=CsvPreviewResult)
async def previsualizar_importacion(
    payload: str = Form(..., description="JSON con mapping y options"),
    file: UploadFile = File(..., description="CSV a previsualizar"),
    db: Session = Depends(get_db),
):
    """Genera una previsualización sin escribir en la base de datos."""

    mapping, options = _parse_payload(payload)
    contenido = await file.read()
    return preview_import(contenido, mapping, options, db)


@router.post("/apply", response_model=CsvImportResult)
async def ejecutar_importacion(
    payload: str = Form(..., description="JSON con mapping y options"),
    file: UploadFile = File(..., description="CSV a importar"),
    db: Session = Depends(get_db),
):
    """Aplica la importación de los registros válidos."""

    mapping, options = _parse_payload(payload)
    contenido = await file.read()
    return apply_import(contenido, mapping, options, db)

