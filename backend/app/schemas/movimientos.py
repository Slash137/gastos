"""Esquemas para movimientos y filtros."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MovimientoBase(BaseModel):
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
    """Datos de actualización."""


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
    categoria_id: Optional[int] = None
    tipo_id: Optional[int] = None
    metodo_pago_id: Optional[int] = None
    importe_min: Optional[float] = None
    importe_max: Optional[float] = None
    concepto: Optional[str] = None
