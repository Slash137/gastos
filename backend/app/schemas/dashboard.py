"""Esquemas para el dashboard analítico."""

from pydantic import BaseModel


class KPIs(BaseModel):
    total_ingresos: float
    total_gastos: float
    balance_neto: float
    media_mensual: float
    variacion_mensual: float
    proyeccion_30d: float
    proyeccion_60d: float


class SerieMensual(BaseModel):
    mes_anio: str
    saldo: float


class DistribucionCategoria(BaseModel):
    categoria: str
    total: float


class BalanceAnual(BaseModel):
    anio: int
    total_gastos: float
    total_ingresos: float


class DashboardResponse(BaseModel):
    kpis: KPIs
    serie_mensual: list[SerieMensual]
    distribucion_categoria: list[DistribucionCategoria]
    balance_anual: list[BalanceAnual]
