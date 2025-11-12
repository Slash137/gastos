"""Pruebas iniciales para el endpoint de salud del backend."""

from fastapi.testclient import TestClient

from backend.app.main import app


def test_healthcheck_returns_ok_status() -> None:
    """El endpoint `/health` debe responder con un estado exitoso."""

    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200, "La API debería responder HTTP 200"
    assert response.json() == {"status": "ok"}, "La carga útil debe indicar estado 'ok'"
