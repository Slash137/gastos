"""Exporta los esquemas de dominio."""

from backend.app.schemas.categorias import CategoriaCreate, CategoriaRead, CategoriaUpdate
from backend.app.schemas.dashboard import (
    DashboardCategoryPoint,
    DashboardFiltro,
    DashboardMonthlyPoint,
    DashboardSummary,
    DashboardYearPoint,
)
from backend.app.schemas.metodos_pago import MetodoPagoCreate, MetodoPagoRead, MetodoPagoUpdate
from backend.app.schemas.movimientos import MovimientoCreate, MovimientoFiltro, MovimientoRead, MovimientoUpdate
from backend.app.schemas.reglas import ReglaCreate, ReglaRead, ReglaUpdate
from backend.app.schemas.tipos import TipoMovimientoCreate, TipoMovimientoRead, TipoMovimientoUpdate

__all__ = [
    "CategoriaCreate",
    "CategoriaRead",
    "CategoriaUpdate",
    "DashboardCategoryPoint",
    "DashboardFiltro",
    "DashboardMonthlyPoint",
    "DashboardSummary",
    "DashboardYearPoint",
    "MetodoPagoCreate",
    "MetodoPagoRead",
    "MetodoPagoUpdate",
    "MovimientoCreate",
    "MovimientoFiltro",
    "MovimientoRead",
    "MovimientoUpdate",
    "ReglaCreate",
    "ReglaRead",
    "ReglaUpdate",
    "TipoMovimientoCreate",
    "TipoMovimientoRead",
    "TipoMovimientoUpdate",
]
