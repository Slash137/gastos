"""Aplicación principal del backend.

Este paquete albergará los módulos del servicio FastAPI encargado de
gestionar el ciclo de vida de la aplicación de gastos.
"""

from .main import create_app

__all__ = ["create_app"]
