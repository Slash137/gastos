"""Verificación de filtros en listado de movimientos."""


def test_filtro_por_fecha_y_importe(client):
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

    resp = client.get("/movimientos", params={"fecha_desde": "2024-03-01"})
    assert resp.status_code == 200
    resultados = resp.json()
    assert len(resultados) == 1
    assert resultados[0]["concepto"] == "Venta"

    resp = client.get("/movimientos", params={"importe_min": 0})
    assert resp.status_code == 200
    positivos = resp.json()
    assert all(item["importe"] >= 0 for item in positivos)
