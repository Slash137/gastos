"""Esquemas para métodos de pago."""

from pydantic import BaseModel, ConfigDict


class MetodoPagoBase(BaseModel):
    nombre: str


class MetodoPagoCreate(MetodoPagoBase):
    """Datos de creación."""


class MetodoPagoUpdate(MetodoPagoBase):
    """Datos de actualización."""


class MetodoPagoRead(MetodoPagoBase):
    """Representación de salida."""

    model_config = ConfigDict(from_attributes=True)
    id: int
