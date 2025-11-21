"""Verificación de filtros en listado de movimientos."""

import csv
from io import StringIO


def _crear_movimientos(client):
    datos = [
        {
            "fecha": "2024-02-01",
            "concepto": "Cafetería",
            "importe": -5.5,
            "saldo": 500,
            "tipo_id": 1,
            "categoria_id": 1,
            "metodo_pago_id": 1,
            "notas": "",
        },
        {
            "fecha": "2024-03-10",
            "concepto": "Venta",
            "importe": 200,
            "saldo": 700,
            "tipo_id": 2,
            "categoria_id": 1,
            "metodo_pago_id": 1,
            "notas": "",
        },
    ]
    for payload in datos:
        resp = client.post("/movimientos", json=payload)
        assert resp.status_code == 201


def test_filtro_por_fecha_y_importe(client):
    _crear_movimientos(client)

    resp = client.get("/movimientos", params={"fecha_desde": "2024-03-01"})
    assert resp.status_code == 200
    resultados = resp.json()
    assert resultados["total_items"] == 1
    assert resultados["items"][0]["concepto"] == "Venta"

    resp = client.get("/movimientos", params={"importe_min": 0})
    assert resp.status_code == 200
    positivos = resp.json()["items"]
    assert all(item["importe"] >= 0 for item in positivos)


def test_export_filtra_concepto(client):
    _crear_movimientos(client)
    resp = client.get("/movimientos/export", params={"search": "cafeter"})
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "text/csv"

    contenido = resp.content.decode("utf-8")
    filas = list(csv.reader(StringIO(contenido)))
    assert filas[0] == [
        "fecha",
        "concepto",
        "importe",
        "saldo",
        "tipo_nombre",
        "categoria_nombre",
        "metodo_pago_nombre",
        "notas",
    ]
    assert len(filas) == 2  # cabecera + 1 fila
    assert filas[1][1] == "Cafetería"
