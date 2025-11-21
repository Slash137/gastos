"""Fixtures compartidas para pruebas."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.database import Base, get_db
from backend.app.main import create_app
from backend.app.models import Categoria, MetodoPago, TipoMovimiento

# Configuramos una base de datos en memoria para aislar las pruebas.
engine_test = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine_test, autoflush=False, autocommit=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine_test)
    session = TestingSessionLocal()
    # Insertamos datos base para relaciones FK.
    gasto = TipoMovimiento(id=1, nombre="Gasto")
    ingreso = TipoMovimiento(id=2, nombre="Ingreso")
    categoria = Categoria(id=1, nombre="General", es_fijo=False)
    metodo = MetodoPago(id=1, nombre="Tarjeta")
    session.add_all([gasto, ingreso, categoria, metodo])
    session.commit()
    session.close()
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture()
def client():
    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
