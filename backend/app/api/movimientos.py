"""Rutas CRUD con filtros y exploración avanzada para movimientos."""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models import Movimiento
from backend.app.schemas.movimientos import (
    MovimientoCreate,
    MovimientoFiltro,
    MovimientoInlineUpdate,
    MovimientoListItem,
    MovimientoListResponse,
    MovimientoRead,
    MovimientoUpdate,
)
from backend.app.services.movimientos import (
    actualizar_movimiento,
    actualizar_movimiento_inline,
    borrar_movimiento,
    crear_movimiento,
    exportar_movimientos,
    listar_movimientos,
)

router = APIRouter(prefix="/movimientos", tags=["movimientos"])


def _obtener_movimiento(db: Session, movimiento_id: int) -> Movimiento:
    movimiento = db.get(Movimiento, movimiento_id)
    if not movimiento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movimiento no encontrado")
    return movimiento


@router.get("", response_model=MovimientoListResponse)
def obtener_movimientos(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    sort_by: Optional[str] = Query(default=None),
    sort_dir: Optional[str] = Query(default=None, pattern="^(asc|desc)$"),
    fecha_desde: Optional[date] = Query(default=None),
    fecha_hasta: Optional[date] = Query(default=None),
    categoria_ids: Optional[str] = Query(default=None),
    tipo_ids: Optional[str] = Query(default=None),
    metodo_pago_ids: Optional[str] = Query(default=None),
    importe_min: Optional[float] = Query(default=None),
    importe_max: Optional[float] = Query(default=None),
    search: Optional[str] = Query(default=None),
    solo_gastos_fijos: Optional[bool] = Query(default=None),
    solo_gastos_variables: Optional[bool] = Query(default=None),
    db: Session = Depends(get_db),
):
    """Retorna movimientos filtrados, ordenados y paginados con agregados."""

    filtros = MovimientoFiltro(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        categoria_ids=[int(x) for x in categoria_ids.split(",")] if categoria_ids else None,
        tipo_ids=[int(x) for x in tipo_ids.split(",")] if tipo_ids else None,
        metodo_pago_ids=[int(x) for x in metodo_pago_ids.split(",")] if metodo_pago_ids else None,
        importe_min=importe_min,
        importe_max=importe_max,
        concepto=search,
        solo_gastos_fijos=solo_gastos_fijos,
        solo_gastos_variables=solo_gastos_variables,
    )
    return listar_movimientos(db, filtros, page=page, page_size=page_size, sort_by=sort_by, sort_dir=sort_dir)


@router.get("/{movimiento_id}", response_model=MovimientoRead)
def obtener_movimiento(movimiento_id: int, db: Session = Depends(get_db)):
    """Devuelve un movimiento individual."""

    return _obtener_movimiento(db, movimiento_id)


@router.post("", response_model=MovimientoRead, status_code=status.HTTP_201_CREATED)
def crear(datos: MovimientoCreate, db: Session = Depends(get_db)):
    """Crea un movimiento."""

    return crear_movimiento(db, datos)


@router.put("/{movimiento_id}", response_model=MovimientoRead)
def actualizar(movimiento_id: int, datos: MovimientoUpdate, db: Session = Depends(get_db)):
    """Actualiza un movimiento."""

    _obtener_movimiento(db, movimiento_id)
    return actualizar_movimiento(db, movimiento_id, datos)


@router.patch("/{movimiento_id}", response_model=MovimientoListItem)
def actualizar_inline(movimiento_id: int, datos: MovimientoInlineUpdate, db: Session = Depends(get_db)):
    """Actualiza parcialmente un movimiento desde edición inline."""

    _obtener_movimiento(db, movimiento_id)
    try:
        return actualizar_movimiento_inline(db, movimiento_id, datos)
    except ValueError as exc:  # mantiene mensajes claros para el cliente
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/{movimiento_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(movimiento_id: int, db: Session = Depends(get_db)):
    """Elimina un movimiento."""

    _obtener_movimiento(db, movimiento_id)
    borrar_movimiento(db, movimiento_id)


@router.get("/export", response_class=Response)
def exportar(
    fecha_desde: Optional[date] = Query(default=None),
    fecha_hasta: Optional[date] = Query(default=None),
    categoria_ids: Optional[str] = Query(default=None),
    tipo_ids: Optional[str] = Query(default=None),
    metodo_pago_ids: Optional[str] = Query(default=None),
    importe_min: Optional[float] = Query(default=None),
    importe_max: Optional[float] = Query(default=None),
    search: Optional[str] = Query(default=None),
    solo_gastos_fijos: Optional[bool] = Query(default=None),
    solo_gastos_variables: Optional[bool] = Query(default=None),
    db: Session = Depends(get_db),
):
    """Exporta a CSV los movimientos filtrados. Usa el mismo pipeline de filtros que el listado."""

    filtros = MovimientoFiltro(
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        categoria_ids=[int(x) for x in categoria_ids.split(",")] if categoria_ids else None,
        tipo_ids=[int(x) for x in tipo_ids.split(",")] if tipo_ids else None,
        metodo_pago_ids=[int(x) for x in metodo_pago_ids.split(",")] if metodo_pago_ids else None,
        importe_min=importe_min,
        importe_max=importe_max,
        concepto=search,
        solo_gastos_fijos=solo_gastos_fijos,
        solo_gastos_variables=solo_gastos_variables,
    )

    items = exportar_movimientos(db, filtros)

    def generar_csv():
        import csv
        from io import StringIO

        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow([
            "fecha",
            "concepto",
            "importe",
            "saldo",
            "tipo_nombre",
            "categoria_nombre",
            "metodo_pago_nombre",
            "notas",
        ])
        for item in items:
            writer.writerow(
                [
                    item.fecha,
                    item.concepto,
                    item.importe,
                    item.saldo,
                    item.tipo_nombre,
                    item.categoria_nombre,
                    item.metodo_pago_nombre,
                    item.notas or "",
                ]
            )
        buffer.seek(0)
        yield buffer.read()

    headers = {"Content-Type": "text/csv", "Content-Disposition": "attachment; filename=movimientos.csv"}
    return StreamingResponse(generar_csv(), headers=headers)
