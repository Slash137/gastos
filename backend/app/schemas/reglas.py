"""Esquemas para reglas de autocategorización."""

from pydantic import BaseModel, ConfigDict

from backend.app.models.entities import CampoObjetivo, TipoMatch


class ReglaBase(BaseModel):
    pattern: str
    campo_objetivo: CampoObjetivo
    tipo_match: TipoMatch = TipoMatch.contains
    categoria_id: int


class ReglaCreate(ReglaBase):
    """Datos de creación de reglas."""


class ReglaUpdate(ReglaBase):
    """Datos de actualización."""


class ReglaRead(ReglaBase):
    """Representación serializada."""

    model_config = ConfigDict(from_attributes=True)
    id: int
