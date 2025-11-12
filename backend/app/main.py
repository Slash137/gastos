"""Punto de entrada de la aplicación FastAPI.

En esta etapa inicial exponemos un endpoint de salud básico que servirá
para validar que la infraestructura del backend está correctamente
configurada. A medida que el proyecto avance, este módulo se encargará
de ensamblar routers, dependencias y configuraciones comunes.
"""

from fastapi import FastAPI


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

    @app.get("/health", tags=["estado"], summary="Verificar estado del servicio")
    async def healthcheck() -> dict[str, str]:
        """Endpoint mínimo para confirmar la disponibilidad del backend.

        La ruta devuelve un diccionario con un mensaje estático. Más
        adelante podremos extender esta respuesta con información sobre
        el estado de la base de datos o dependencias externas.
        """

        return {"status": "ok"}

    return app


app = create_app()
"""Instancia global usada por servidores ASGI como Uvicorn."""
