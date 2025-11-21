"""Esquemas para movimientos y filtros."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MovimientoBase(BaseModel):
    """Campos comunes para la creación y lectura de movimientos."""

    fecha: date
    concepto: str
    importe: float
    saldo: Optional[float] = None
    tipo_id: int
    categoria_id: int
    metodo_pago_id: int
    notas: Optional[str] = None


class MovimientoCreate(MovimientoBase):
    """Datos de creación."""


class MovimientoUpdate(MovimientoBase):
    """Datos de actualización completa."""


class MovimientoInlineUpdate(BaseModel):
    """Permite actualizaciones parciales desde el frontend (inline edit)."""

    categoria_id: Optional[int] = None
    notas: Optional[str] = None
    metodo_pago_id: Optional[int] = None


class MovimientoRead(MovimientoBase):
    """Salida serializada con campos derivados."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    anio: int
    mes: int
    mes_anio: str


class MovimientoFiltro(BaseModel):
    """Filtros disponibles para búsquedas en el endpoint de movimientos."""

    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    categoria_ids: Optional[list[int]] = Field(default=None, description="Listado de categorías a incluir")
    tipo_ids: Optional[list[int]] = None
    metodo_pago_ids: Optional[list[int]] = None
    importe_min: Optional[float] = None
    importe_max: Optional[float] = None
    concepto: Optional[str] = None
    solo_gastos_fijos: Optional[bool] = None
    solo_gastos_variables: Optional[bool] = None


class MovimientoListItem(BaseModel):
    """Estructura enriquecida devuelta en los listados."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    fecha: date
    concepto: str
    importe: float
    saldo: Optional[float]
    tipo_id: int
    tipo_nombre: str
    categoria_id: Optional[int]
    categoria_nombre: Optional[str]
    categoria_es_fijo: Optional[bool]
    metodo_pago_id: Optional[int]
    metodo_pago_nombre: Optional[str]
    notas: Optional[str]
    mes_anio: Optional[str] = None


class MovimientoAggregates(BaseModel):
    """Totales calculados en servidor para los filtros activos."""

    total_registros: int
    total_importe: float
    total_gastos: float
    total_ingresos: float
    promedio_mensual: Optional[float] = None


class MovimientoListResponse(BaseModel):
    """Respuesta paginada de movimientos con agregados."""

    items: list[MovimientoListItem]
    page: int
    page_size: int
    total_items: int
    total_pages: int
    aggregates: MovimientoAggregates
