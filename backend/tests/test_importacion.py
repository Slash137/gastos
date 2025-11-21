"""Pruebas de extremo a extremo del flujo de importación CSV."""

import json


def _payload(mapping, options):
    return json.dumps({"mapping": mapping, "options": options})


def test_analyze_csv(client):
    contenido = """fecha,concepto,importe\n2024-01-01,Compra,-10\n"""
    archivo = ("simple.csv", contenido, "text/csv")
    resp = client.post("/import/analyze", files={"file": archivo})
    assert resp.status_code == 200
    data = resp.json()
    assert "columns" in data and data["columns"] == ["fecha", "concepto", "importe"]
    assert data["format"] == "generic"
    assert data["sample"][0]["concepto"] == "Compra"


def test_preview_detecta_error_y_duplicado(client):
    # Primero insertamos un movimiento existente para probar duplicados.
    contenido_inicial = """fecha,concepto,importe\n2024-01-01,Compra,-10\n"""
    mapping = {"fecha_col": "fecha", "concepto_col": "concepto", "importe_col": "importe"}
    options = {
        "default_categoria_id": 1,
        "default_metodo_pago_id": 1,
        "detectar_tipo_por_signo": True,
    }
    client.post(
        "/import/apply",
        files={
            "file": ("base.csv", contenido_inicial, "text/csv"),
            "payload": (None, _payload(mapping, options), "application/json"),
        },
    )

    contenido = """fecha,concepto,importe\n2024-01-02,Restaurante,-20\n2024-13-01,ErrorFecha,-5\n2024-01-01,Compra,-10\n"""
    resp = client.post(
        "/import/preview",
        files={
            "file": ("preview.csv", contenido, "text/csv"),
            "payload": (None, _payload(mapping, options), "application/json"),
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["error_rows"] == 1
    assert data["duplicate_rows"] >= 1
    assert any(row["is_duplicate"] for row in data["rows"])


def test_apply_csv_crea_movimientos(client):
    contenido = """fecha,concepto,importe,notas\n2024-02-01,Supermercado,-50,Compra semanal\n2024-02-05,Nomina,1500,Ingreso mensual\n"""
    mapping = {
        "fecha_col": "fecha",
        "concepto_col": "concepto",
        "importe_col": "importe",
        "notas_col": "notas",
    }
    options = {
        "default_categoria_id": 1,
        "default_metodo_pago_id": 1,
        "detectar_tipo_por_signo": True,
    }
    resp = client.post(
        "/import/apply",
        files={
            "file": ("movimientos.csv", contenido, "text/csv"),
            "payload": (None, _payload(mapping, options), "application/json"),
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["imported"] == 2

    lista = client.get("/movimientos")
    assert lista.status_code == 200
    assert len(lista.json()) >= 2

