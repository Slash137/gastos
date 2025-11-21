"""Esquemas Pydantic para tipos de movimiento."""

from pydantic import BaseModel, ConfigDict


class TipoMovimientoBase(BaseModel):
    nombre: str


class TipoMovimientoCreate(TipoMovimientoBase):
    """Datos necesarios para crear un tipo."""


class TipoMovimientoUpdate(TipoMovimientoBase):
    """Datos para actualizar un tipo existente."""


class TipoMovimientoRead(TipoMovimientoBase):
    """Representación serializada de un tipo."""

    model_config = ConfigDict(from_attributes=True)
    id: int
