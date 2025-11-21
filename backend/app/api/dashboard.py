"""Endpoints de analítica y KPIs para el dashboard.

Se divide la información en endpoints especializados para que el frontend
pueda componer gráficos y KPIs al estilo de una herramienta BI ligera.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from typing import Optional
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.dashboard import (
    DashboardCategoryPoint,
    DashboardFiltro,
    DashboardMonthlyPoint,
    DashboardSummary,
    DashboardYearPoint,
)
from backend.app.services import dashboard as dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _extraer_filtros(
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    categoria_ids: Optional[str] = None,
    tipo_ids: Optional[str] = None,
    metodo_pago_ids: Optional[str] = None,
    solo_gastos_fijos: Optional[bool] = None,
    solo_gastos_variables: Optional[bool] = None,
) -> DashboardFiltro:
    """Convierte query params en un `DashboardFiltro` homogéneo.

    Se utiliza una función auxiliar en vez de dependencias declarativas para
    mantener control total sobre la conversión de listas y permitir valores
    opcionales.
    """

    def _parse_lista(val: Optional[str]) -> Optional[list[int]]:
        if not val:
            return None
        return [int(item) for item in val.split(",") if item]

    return DashboardFiltro(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        categoria_ids=_parse_lista(categoria_ids),
        tipo_ids=_parse_lista(tipo_ids),
        metodo_pago_ids=_parse_lista(metodo_pago_ids),
        solo_gastos_fijos=solo_gastos_fijos,
        solo_gastos_variables=solo_gastos_variables,
    )


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    categoria_ids: Optional[str] = None,
    tipo_ids: Optional[str] = None,
    metodo_pago_ids: Optional[str] = None,
    solo_gastos_fijos: Optional[bool] = None,
    solo_gastos_variables: Optional[bool] = None,
    db: Session = Depends(get_db),
) -> DashboardSummary:
    """Calcula los KPIs principales del dashboard."""

    filtros = _extraer_filtros(
        fecha_desde,
        fecha_hasta,
        categoria_ids,
        tipo_ids,
        metodo_pago_ids,
        solo_gastos_fijos,
        solo_gastos_variables,
    )
    return dashboard_service.obtener_resumen(db, filtros)


@router.get("/monthly", response_model=list[DashboardMonthlyPoint])
def get_dashboard_monthly(
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    categoria_ids: Optional[str] = None,
    tipo_ids: Optional[str] = None,
    metodo_pago_ids: Optional[str] = None,
    solo_gastos_fijos: Optional[bool] = None,
    solo_gastos_variables: Optional[bool] = None,
    db: Session = Depends(get_db),
) -> list[DashboardMonthlyPoint]:
    """Serie mensual de gastos, ingresos y balance."""

    filtros = _extraer_filtros(
        fecha_desde,
        fecha_hasta,
        categoria_ids,
        tipo_ids,
        metodo_pago_ids,
        solo_gastos_fijos,
        solo_gastos_variables,
    )
    return dashboard_service.obtener_serie_mensual(db, filtros)


@router.get("/by-category", response_model=list[DashboardCategoryPoint])
def get_dashboard_by_category(
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    categoria_ids: Optional[str] = None,
    tipo_ids: Optional[str] = None,
    metodo_pago_ids: Optional[str] = None,
    solo_gastos_fijos: Optional[bool] = None,
    solo_gastos_variables: Optional[bool] = None,
    db: Session = Depends(get_db),
) -> list[DashboardCategoryPoint]:
    """Distribución de importes por categoría para gráficas de pastel."""

    filtros = _extraer_filtros(
        fecha_desde,
        fecha_hasta,
        categoria_ids,
        tipo_ids,
        metodo_pago_ids,
        solo_gastos_fijos,
        solo_gastos_variables,
    )
    return dashboard_service.obtener_por_categoria(db, filtros)


@router.get("/yearly", response_model=list[DashboardYearPoint])
def get_dashboard_yearly(
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    categoria_ids: Optional[str] = None,
    tipo_ids: Optional[str] = None,
    metodo_pago_ids: Optional[str] = None,
    solo_gastos_fijos: Optional[bool] = None,
    solo_gastos_variables: Optional[bool] = None,
    db: Session = Depends(get_db),
) -> list[DashboardYearPoint]:
    """Agregación anual de gastos/ingresos/balance."""

    filtros = _extraer_filtros(
        fecha_desde,
        fecha_hasta,
        categoria_ids,
        tipo_ids,
        metodo_pago_ids,
        solo_gastos_fijos,
        solo_gastos_variables,
    )
    return dashboard_service.obtener_por_anio(db, filtros)
