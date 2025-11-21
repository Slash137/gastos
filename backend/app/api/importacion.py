"""Endpoint de importación desde CSV."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.services.importador_csv import procesar_csv

router = APIRouter(prefix="/import", tags=["importacion"])


@router.post("/csv")
def importar_csv(
    archivo: UploadFile = File(..., description="Fichero CSV con columnas requeridas"),
    db: Session = Depends(get_db),
):
    """Procesa un archivo CSV y crea movimientos."""

    if not archivo.filename.endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo debe ser CSV")
    resultado = procesar_csv(archivo, db)
    return resultado
