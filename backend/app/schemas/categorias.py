"""Esquemas de categorías."""

from pydantic import BaseModel, ConfigDict


class CategoriaBase(BaseModel):
    nombre: str
    es_fijo: bool = False


class CategoriaCreate(CategoriaBase):
    """Datos de creación."""


class CategoriaUpdate(CategoriaBase):
    """Datos de actualización."""


class CategoriaRead(CategoriaBase):
    """Representación de salida."""

    model_config = ConfigDict(from_attributes=True)
    id: int
