"""Punto de entrada de la aplicación FastAPI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api import categorias, dashboard, health, importacion, metodos_pago, movimientos, reglas, tipos
from backend.app.core.database import Base, engine


def create_app() -> FastAPI:
    """Crear y configurar la instancia principal de FastAPI."""

    app = FastAPI(
        title="Gastos API",
        description=(
            "Servicio backend para la gestión de movimientos bancarios, "
            "categorías y analítica de gastos domésticos."
        ),
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    Base.metadata.create_all(bind=engine)

    app.include_router(health.router)
    app.include_router(importacion.router)
    app.include_router(movimientos.router)
    app.include_router(categorias.router)
    app.include_router(tipos.router)
    app.include_router(metodos_pago.router)
    app.include_router(reglas.router)
    app.include_router(dashboard.router)

    return app


app = create_app()
"""Instancia global usada por servidores ASGI como Uvicorn."""
