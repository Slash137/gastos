"""Rutas para gestionar reglas de autocategorización."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models import ReglaAutoCategoria
from backend.app.schemas.reglas import ReglaCreate, ReglaRead, ReglaUpdate
from backend.app.services.reglas import reaplicar_reglas

router = APIRouter(prefix="/reglas", tags=["reglas"])


def _obtener_regla(db: Session, regla_id: int) -> ReglaAutoCategoria:
    regla = db.get(ReglaAutoCategoria, regla_id)
    if not regla:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regla no encontrada")
    return regla


@router.get("", response_model=list[ReglaRead])
def listar_reglas(db: Session = Depends(get_db)):
    """Obtiene todas las reglas configuradas."""

    return db.query(ReglaAutoCategoria).all()


@router.post("", response_model=ReglaRead, status_code=status.HTTP_201_CREATED)
def crear_regla(datos: ReglaCreate, db: Session = Depends(get_db)):
    """Crea una regla nueva."""

    regla = ReglaAutoCategoria(**datos.model_dump())
    db.add(regla)
    db.commit()
    db.refresh(regla)
    return regla


@router.put("/{regla_id}", response_model=ReglaRead)
def actualizar_regla(regla_id: int, datos: ReglaUpdate, db: Session = Depends(get_db)):
    """Actualiza una regla existente."""

    regla = _obtener_regla(db, regla_id)
    for campo, valor in datos.model_dump().items():
        setattr(regla, campo, valor)
    db.commit()
    db.refresh(regla)
    return regla


@router.delete("/{regla_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_regla(regla_id: int, db: Session = Depends(get_db)):
    """Elimina una regla."""

    regla = _obtener_regla(db, regla_id)
    db.delete(regla)
    db.commit()


@router.post("/reaplicar", summary="Reaplicar reglas a todos los movimientos")
def reaplicar(db: Session = Depends(get_db)):
    """Fuerza la reaplicación de reglas a cada movimiento existente."""

    actualizados = reaplicar_reglas(db)
    return {"movimientos_actualizados": actualizados}
