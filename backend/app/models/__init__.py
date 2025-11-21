"""Modelos ORM del dominio de gastos."""

from backend.app.models.entities import Categoria, MetodoPago, Movimiento, ReglaAutoCategoria, TipoMovimiento

__all__ = [
    "Categoria",
    "MetodoPago",
    "Movimiento",
    "ReglaAutoCategoria",
    "TipoMovimiento",
]
