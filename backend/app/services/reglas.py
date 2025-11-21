"""Aplicación de reglas de autocategorización."""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.app.models import Movimiento, ReglaAutoCategoria


def aplicar_reglas_movimiento(db: Session, movimiento: Movimiento) -> None:
    """Asigna categorías según reglas definidas.

    La estrategia actual aplica reglas secuencialmente con coincidencia
    "contains" insensible a mayúsculas. En futuras versiones se pueden añadir
    patrones avanzados o prioridades.
    """

    reglas = db.query(ReglaAutoCategoria).all()
    for regla in reglas:
        valor_objetivo = getattr(movimiento, regla.campo_objetivo.value) or ""
        if regla.tipo_match.value == "contains" and regla.pattern.lower() in valor_objetivo.lower():
            movimiento.categoria_id = regla.categoria_id


def reaplicar_reglas(db: Session) -> int:
    """Reaplica las reglas a todos los movimientos existentes.

    Returns:
        int: número de movimientos actualizados.
    """

    reglas = db.query(ReglaAutoCategoria).all()
    movimientos = db.query(Movimiento).all()
    actualizados = 0
    for movimiento in movimientos:
        categoria_original = movimiento.categoria_id
        for regla in reglas:
            valor_objetivo = getattr(movimiento, regla.campo_objetivo.value) or ""
            if regla.tipo_match.value == "contains" and regla.pattern.lower() in valor_objetivo.lower():
                movimiento.categoria_id = regla.categoria_id
        if movimiento.categoria_id != categoria_original:
            actualizados += 1
    db.commit()
    return actualizados
