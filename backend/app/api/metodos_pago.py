"""Endpoints CRUD para métodos de pago."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models import MetodoPago
from backend.app.schemas.metodos_pago import MetodoPagoCreate, MetodoPagoRead, MetodoPagoUpdate

router = APIRouter(prefix="/metodos-pago", tags=["metodos-pago"])


def _obtener_metodo(db: Session, metodo_id: int) -> MetodoPago:
    metodo = db.get(MetodoPago, metodo_id)
    if not metodo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Método de pago no encontrado")
    return metodo


@router.get("", response_model=list[MetodoPagoRead])
def listar_metodos(db: Session = Depends(get_db)):
    """Lista métodos de pago."""

    return db.query(MetodoPago).all()


@router.post("", response_model=MetodoPagoRead, status_code=status.HTTP_201_CREATED)
def crear_metodo(datos: MetodoPagoCreate, db: Session = Depends(get_db)):
    """Crea un método de pago."""

    metodo = MetodoPago(**datos.model_dump())
    db.add(metodo)
    db.commit()
    db.refresh(metodo)
    return metodo


@router.put("/{metodo_id}", response_model=MetodoPagoRead)
def actualizar_metodo(metodo_id: int, datos: MetodoPagoUpdate, db: Session = Depends(get_db)):
    """Actualiza un método de pago."""

    metodo = _obtener_metodo(db, metodo_id)
    for campo, valor in datos.model_dump().items():
        setattr(metodo, campo, valor)
    db.commit()
    db.refresh(metodo)
    return metodo


@router.delete("/{metodo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_metodo(metodo_id: int, db: Session = Depends(get_db)):
    """Elimina un método de pago."""

    metodo = _obtener_metodo(db, metodo_id)
    db.delete(metodo)
    db.commit()
