"""Servicios de dominio para movimientos."""

from __future__ import annotations

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from backend.app.models import Movimiento
from backend.app.schemas.movimientos import MovimientoCreate, MovimientoFiltro, MovimientoUpdate
from backend.app.services.reglas import aplicar_reglas_movimiento


def aplicar_filtros(base_query, filtros: MovimientoFiltro):
    """Aplica filtros dinámicos a la consulta base."""

    condiciones = []
    if filtros.fecha_desde:
        condiciones.append(Movimiento.fecha >= filtros.fecha_desde)
    if filtros.fecha_hasta:
        condiciones.append(Movimiento.fecha <= filtros.fecha_hasta)
    if filtros.categoria_id:
        condiciones.append(Movimiento.categoria_id == filtros.categoria_id)
    if filtros.tipo_id:
        condiciones.append(Movimiento.tipo_id == filtros.tipo_id)
    if filtros.metodo_pago_id:
        condiciones.append(Movimiento.metodo_pago_id == filtros.metodo_pago_id)
    if filtros.importe_min is not None:
        condiciones.append(Movimiento.importe >= filtros.importe_min)
    if filtros.importe_max is not None:
        condiciones.append(Movimiento.importe <= filtros.importe_max)
    if filtros.concepto:
        like_expr = f"%{filtros.concepto.lower()}%"
        condiciones.append(Movimiento.concepto.ilike(like_expr))

    if condiciones:
        base_query = base_query.where(and_(*condiciones))
    return base_query


def listar_movimientos(db: Session, filtros: MovimientoFiltro | None = None) -> list[Movimiento]:
    """Obtiene movimientos aplicando filtros opcionales."""

    query = select(Movimiento)
    if filtros:
        query = aplicar_filtros(query, filtros)
    return list(db.scalars(query))


def crear_movimiento(db: Session, datos: MovimientoCreate) -> Movimiento:
    """Crea un movimiento y aplica reglas automáticas."""

    movimiento = Movimiento(**datos.model_dump())
    movimiento.rellenar_campos_derivados()
    aplicar_reglas_movimiento(db, movimiento)
    db.add(movimiento)
    db.commit()
    db.refresh(movimiento)
    return movimiento


def actualizar_movimiento(db: Session, movimiento_id: int, datos: MovimientoUpdate) -> Movimiento:
    """Actualiza un movimiento existente."""

    movimiento = db.get(Movimiento, movimiento_id)
    if not movimiento:
        raise ValueError("Movimiento no encontrado")
    for campo, valor in datos.model_dump().items():
        setattr(movimiento, campo, valor)
    movimiento.rellenar_campos_derivados()
    aplicar_reglas_movimiento(db, movimiento)
    db.commit()
    db.refresh(movimiento)
    return movimiento


def borrar_movimiento(db: Session, movimiento_id: int) -> None:
    """Elimina un movimiento."""

    movimiento = db.get(Movimiento, movimiento_id)
    if movimiento:
        db.delete(movimiento)
        db.commit()
