"""Rutas dedicadas a comprobar el estado del servicio."""

from fastapi import APIRouter

# Instanciamos un router específico sin prefijo para que el endpoint se
# exponga en la raíz del servicio. A medida que se añadan rutas, podremos
# reutilizar esta estructura para agruparlas por dominio funcional.
router = APIRouter(tags=["estado"])


@router.get("/health", summary="Verificar estado del servicio")
async def healthcheck() -> dict[str, str]:
    """Endpoint mínimo para confirmar la disponibilidad del backend."""

    # Devolvemos una respuesta simple que puede ampliarse en el futuro con
    # verificaciones de base de datos o servicios externos.
    return {"status": "ok"}
