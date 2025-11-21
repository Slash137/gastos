"""Endpoints CRUD para tipos de movimiento."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models import TipoMovimiento
from backend.app.schemas.tipos import TipoMovimientoCreate, TipoMovimientoRead, TipoMovimientoUpdate

router = APIRouter(prefix="/tipos", tags=["tipos"])


def _obtener_tipo(db: Session, tipo_id: int) -> TipoMovimiento:
    """Busca un tipo o lanza 404."""

    tipo = db.get(TipoMovimiento, tipo_id)
    if not tipo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo no encontrado")
    return tipo


@router.get("", response_model=list[TipoMovimientoRead])
def listar_tipos(db: Session = Depends(get_db)):
    """Lista todos los tipos de movimiento."""

    return db.query(TipoMovimiento).all()


@router.post("", response_model=TipoMovimientoRead, status_code=status.HTTP_201_CREATED)
def crear_tipo(datos: TipoMovimientoCreate, db: Session = Depends(get_db)):
    """Crea un tipo de movimiento."""

    tipo = TipoMovimiento(**datos.model_dump())
    db.add(tipo)
    db.commit()
    db.refresh(tipo)
    return tipo


@router.put("/{tipo_id}", response_model=TipoMovimientoRead)
def actualizar_tipo(tipo_id: int, datos: TipoMovimientoUpdate, db: Session = Depends(get_db)):
    """Actualiza un tipo existente."""

    tipo = _obtener_tipo(db, tipo_id)
    for campo, valor in datos.model_dump().items():
        setattr(tipo, campo, valor)
    db.commit()
    db.refresh(tipo)
    return tipo


@router.delete("/{tipo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_tipo(tipo_id: int, db: Session = Depends(get_db)):
    """Elimina un tipo de movimiento."""

    tipo = _obtener_tipo(db, tipo_id)
    db.delete(tipo)
    db.commit()
