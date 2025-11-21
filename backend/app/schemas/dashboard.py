"""Esquemas para el dashboard analítico.

Este módulo define los modelos Pydantic utilizados por los endpoints de
analítica. Se han separado las estructuras por tipo de recurso (resumen,
series temporales, etc.) para ofrecer un contrato de API claro y estable.
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class DashboardFiltro(BaseModel):
    """Filtros disponibles para las vistas agregadas del dashboard."""

    fecha_desde: Optional[date] = Field(default=None, description="Fecha inicial del rango")
    fecha_hasta: Optional[date] = Field(default=None, description="Fecha final del rango")
    categoria_ids: Optional[list[int]] = Field(default=None, description="Categorías a incluir")
    tipo_ids: Optional[list[int]] = Field(default=None, description="Tipos de movimiento a incluir")
    metodo_pago_ids: Optional[list[int]] = Field(default=None, description="Métodos de pago a incluir")
    solo_gastos_fijos: Optional[bool] = Field(
        default=None, description="Limitar a gastos marcados como fijos"
    )
    solo_gastos_variables: Optional[bool] = Field(
        default=None, description="Limitar a gastos variables"
    )


class DashboardSummary(BaseModel):
    """KPIs principales del periodo filtrado."""

    total_gastos: float
    total_ingresos: float
    balance_neto: float
    gasto_medio_mensual: float
    variacion_mensual_porcentaje: Optional[float]
    proyeccion_saldo_30d: Optional[float]
    proyeccion_saldo_60d: Optional[float]


class DashboardMonthlyPoint(BaseModel):
    """Punto de la serie mensual para gráficos de línea o área."""

    mes_anio: str
    total_gastos: float
    total_ingresos: float
    balance_neto: float


class DashboardCategoryPoint(BaseModel):
    """Distribución de importes por categoría."""

    categoria_id: Optional[int]
    categoria_nombre: str
    total_importe: float
    total_gastos: float
    total_ingresos: float
    porcentaje_sobre_total: float


class DashboardYearPoint(BaseModel):
    """Totales anuales para la comparación entre años."""

    anio: int
    total_gastos: float
    total_ingresos: float
    balance_neto: float
