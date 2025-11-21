"""Pruebas para los endpoints del dashboard analítico."""

import pytest


def _cargar_movimientos_demo(client):
    """Carga un pequeño set de datos multi-mes para validar agregaciones."""

    movimientos = [
        {
            "fecha": "2024-01-10",
            "concepto": "Compra supermercado",
            "importe": -100.0,
            "saldo": 400.0,
            "tipo_id": 1,
            "categoria_id": 1,
            "metodo_pago_id": 1,
            "notas": "", 
        },
        {
            "fecha": "2024-01-15",
            "concepto": "Nómina",
            "importe": 500.0,
            "saldo": 900.0,
            "tipo_id": 2,
            "categoria_id": 1,
            "metodo_pago_id": 1,
            "notas": "", 
        },
        {
            "fecha": "2024-02-05",
            "concepto": "Alquiler",
            "importe": -200.0,
            "saldo": 700.0,
            "tipo_id": 1,
            "categoria_id": 1,
            "metodo_pago_id": 1,
            "notas": "", 
        },
        {
            "fecha": "2024-02-06",
            "concepto": "Ingreso extra",
            "importe": 400.0,
            "saldo": 1100.0,
            "tipo_id": 2,
            "categoria_id": 1,
            "metodo_pago_id": 1,
            "notas": "", 
        },
        {
            "fecha": "2024-03-01",
            "concepto": "Restaurante",
            "importe": -50.0,
            "saldo": 1050.0,
            "tipo_id": 1,
            "categoria_id": 1,
            "metodo_pago_id": 1,
            "notas": "", 
        },
    ]
    for movimiento in movimientos:
        resp = client.post("/movimientos", json=movimiento)
        assert resp.status_code == 201


def test_dashboard_summary(client):
    _cargar_movimientos_demo(client)

    resp = client.get("/dashboard/summary")
    assert resp.status_code == 200
    data = resp.json()

    assert data["total_gastos"] == pytest.approx(350.0)
    assert data["total_ingresos"] == pytest.approx(900.0)
    assert data["balance_neto"] == pytest.approx(550.0)
    assert data["gasto_medio_mensual"] == pytest.approx((100 + 200 + 50) / 3)
    assert data["variacion_mensual_porcentaje"] == pytest.approx(-75.0)
    assert data["proyeccion_saldo_30d"] == pytest.approx(733.33, rel=1e-2)
    assert data["proyeccion_saldo_60d"] == pytest.approx(916.66, rel=1e-2)


def test_dashboard_monthly_shape(client):
    _cargar_movimientos_demo(client)

    resp = client.get("/dashboard/monthly")
    assert resp.status_code == 200
    serie = resp.json()

    assert len(serie) == 3
    assert serie[0]["mes_anio"] == "2024-01"
    assert serie[0]["total_gastos"] == pytest.approx(100.0)
    assert serie[0]["total_ingresos"] == pytest.approx(500.0)


def test_dashboard_by_category_percentages(client):
    _cargar_movimientos_demo(client)

    resp = client.get("/dashboard/by-category")
    assert resp.status_code == 200
    categorias = resp.json()

    total_porcentaje = sum(item["porcentaje_sobre_total"] for item in categorias)
    assert total_porcentaje == pytest.approx(100.0)


def test_dashboard_yearly(client):
    _cargar_movimientos_demo(client)

    resp = client.get("/dashboard/yearly")
    assert resp.status_code == 200
    anual = resp.json()

    assert len(anual) == 1
    assert anual[0]["anio"] == 2024
    assert anual[0]["total_gastos"] == pytest.approx(350.0)
    assert anual[0]["total_ingresos"] == pytest.approx(900.0)
    assert anual[0]["balance_neto"] == pytest.approx(550.0)
