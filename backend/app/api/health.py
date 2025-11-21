"""Rutas dedicadas a comprobar el estado del servicio."""

from fastapi import APIRouter

router = APIRouter(tags=["estado"])


@router.get("/health", summary="Verificar estado del servicio")
async def healthcheck() -> dict[str, str]:
    """Endpoint mínimo para confirmar la disponibilidad del backend."""

    return {"status": "ok"}
