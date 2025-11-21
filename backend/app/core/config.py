"""Configuración centralizada de la aplicación."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Ajustes de entorno leídos desde variables o valores por defecto.

    La configuración está pensada para ser simple en desarrollo con SQLite y
    permitir un cambio directo a PostgreSQL mediante la variable
    `DATABASE_URL`. Otros parámetros como `ENVIRONMENT` pueden emplearse para
    ajustar logging o middlewares en futuras iteraciones.
    """

    environment: str = Field(default="development", alias="ENVIRONMENT")
    database_url: str = Field(
        default="sqlite:///./gastos.db",
        alias="DATABASE_URL",
        description="Cadena de conexión SQLAlchemy",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        populate_by_name = True


def get_settings() -> Settings:
    """Retorna una instancia única de configuración."""

    return Settings()
