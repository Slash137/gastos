"""Rutas CRUD con filtros para movimientos."""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models import Movimiento
from backend.app.schemas.movimientos import MovimientoCreate, MovimientoFiltro, MovimientoRead, MovimientoUpdate
from backend.app.services.movimientos import borrar_movimiento, crear_movimiento, listar_movimientos, actualizar_movimiento

router = APIRouter(prefix="/movimientos", tags=["movimientos"])


def _obtener_movimiento(db: Session, movimiento_id: int) -> Movimiento:
    movimiento = db.get(Movimiento, movimiento_id)
    if not movimiento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movimiento no encontrado")
    return movimiento


@router.get("", response_model=list[MovimientoRead])
def obtener_movimientos(
    fecha_desde: Optional[date] = Query(default=None),
    fecha_hasta: Optional[date] = Query(default=None),
    categoria_id: Optional[int] = Query(default=None),
    tipo_id: Optional[int] = Query(default=None),
    metodo_pago_id: Optional[int] = Query(default=None),
    importe_min: Optional[float] = Query(default=None),
    importe_max: Optional[float] = Query(default=None),
    concepto: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    """Retorna movimientos filtrados."""

    filtros = MovimientoFiltro(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        categoria_id=categoria_id,
        tipo_id=tipo_id,
        metodo_pago_id=metodo_pago_id,
        importe_min=importe_min,
        importe_max=importe_max,
        concepto=concepto,
    )
    return listar_movimientos(db, filtros)


@router.get("/{movimiento_id}", response_model=MovimientoRead)
def obtener_movimiento(movimiento_id: int, db: Session = Depends(get_db)):
    """Devuelve un movimiento individual."""

    return _obtener_movimiento(db, movimiento_id)


@router.post("", response_model=MovimientoRead, status_code=status.HTTP_201_CREATED)
def crear(datos: MovimientoCreate, db: Session = Depends(get_db)):
    """Crea un movimiento."""

    return crear_movimiento(db, datos)


@router.put("/{movimiento_id}", response_model=MovimientoRead)
def actualizar(movimiento_id: int, datos: MovimientoUpdate, db: Session = Depends(get_db)):
    """Actualiza un movimiento."""

    _obtener_movimiento(db, movimiento_id)
    return actualizar_movimiento(db, movimiento_id, datos)


@router.delete("/{movimiento_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(movimiento_id: int, db: Session = Depends(get_db)):
    """Elimina un movimiento."""

    _obtener_movimiento(db, movimiento_id)
    borrar_movimiento(db, movimiento_id)
