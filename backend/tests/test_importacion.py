"""Pruebas de importación CSV con validación básica."""


def test_importacion_csv(client):
    contenido = """fecha,concepto,importe,saldo,tipo_id,categoria_id,metodo_pago_id,notas
2024-01-01,Supermercado,-50.5,1000,1,1,1,Compra semanal
2024-01-05,Nómina,1500,2000,2,1,1,Ingreso mensual
"""
    archivo = ("movimientos.csv", contenido, "text/csv")

    respuesta = client.post("/import/csv", files={"archivo": archivo})
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["insertados"] == 2
    assert datos["errores"] == []

    lista = client.get("/movimientos")
    assert lista.status_code == 200
    assert len(lista.json()) == 2
