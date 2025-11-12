"""Colección de routers del servicio FastAPI.

Este paquete agrupará las rutas públicas de la API para facilitar su
registro centralizado en la aplicación principal.
"""

from .health import router as health_router

__all__ = ["health_router"]
