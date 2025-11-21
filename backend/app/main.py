"""Punto de entrada de la aplicación FastAPI.

En esta etapa inicial ensamblamos la instancia principal y registramos
routers especializados, lo que permitirá escalar el backend manteniendo
una separación clara por dominios.
"""

from fastapi import FastAPI

from backend.app.routers import health_router


def create_app() -> FastAPI:
    """Crear y configurar la instancia principal de FastAPI.

    La función encapsula la creación de la aplicación para facilitar
    futuras tareas de testing y permitir que los distintos entornos
    (desarrollo, producción) ajusten parámetros sin duplicar código.

    Returns:
        FastAPI: instancia configurada de la aplicación.
    """

    app = FastAPI(
        title="Gastos API",
        description=(
            "Servicio backend para la gestión de movimientos bancarios, "
            "categorías y analítica de gastos domésticos."
        ),
        version="0.1.0",
    )

    # Registramos las rutas de salud en la aplicación principal. A futuro se
    # añadirá el resto de routers (movimientos, categorías, etc.).
    app.include_router(health_router)

    return app


app = create_app()
"""Instancia global usada por servidores ASGI como Uvicorn."""
