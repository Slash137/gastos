"""Servicios de dominio y utilidades de filtrado para movimientos."""

from __future__ import annotations

from typing import Iterable, Optional

from sqlalchemy import and_, asc, case, desc, func, or_, select
from sqlalchemy.orm import Session

from backend.app.models import Categoria, MetodoPago, Movimiento, TipoMovimiento
from backend.app.schemas.movimientos import (
    MovimientoAggregates,
    MovimientoCreate,
    MovimientoFiltro,
    MovimientoInlineUpdate,
    MovimientoListItem,
    MovimientoListResponse,
    MovimientoUpdate,
)
from backend.app.services.reglas import aplicar_reglas_movimiento


def aplicar_filtros(base_query, filtros: MovimientoFiltro):
    """Aplica filtros dinámicos a la consulta base.

    Se mantiene deliberadamente separada para poder ser reutilizada tanto
    en listados paginados como en exportaciones o cálculos de agregados.
    """

    condiciones = []
    if filtros.fecha_desde:
        condiciones.append(Movimiento.fecha >= filtros.fecha_desde)
    if filtros.fecha_hasta:
        condiciones.append(Movimiento.fecha <= filtros.fecha_hasta)
    if filtros.categoria_ids:
        condiciones.append(Movimiento.categoria_id.in_(filtros.categoria_ids))
    if filtros.tipo_ids:
        condiciones.append(Movimiento.tipo_id.in_(filtros.tipo_ids))
    if filtros.metodo_pago_ids:
        condiciones.append(Movimiento.metodo_pago_id.in_(filtros.metodo_pago_ids))
    if filtros.importe_min is not None:
        condiciones.append(Movimiento.importe >= filtros.importe_min)
    if filtros.importe_max is not None:
        condiciones.append(Movimiento.importe <= filtros.importe_max)
    if filtros.concepto:
        like_expr = f"%{filtros.concepto.lower()}%"
        condiciones.append(
            or_(
                func.lower(Movimiento.concepto).like(like_expr),
                func.lower(Movimiento.notas).like(like_expr),
            )
        )
    if filtros.solo_gastos_fijos:
        condiciones.append(Categoria.es_fijo.is_(True))
    if filtros.solo_gastos_variables:
        condiciones.append(Categoria.es_fijo.is_(False))

    if condiciones:
        base_query = base_query.where(and_(*condiciones))
    return base_query


def _query_base_movimientos():
    """Construye la consulta base con joins necesarios para enriquecer la salida."""

    return (
        select(
            Movimiento,
            Categoria.nombre.label("categoria_nombre"),
            Categoria.es_fijo.label("categoria_es_fijo"),
            TipoMovimiento.nombre.label("tipo_nombre"),
            MetodoPago.nombre.label("metodo_pago_nombre"),
        )
        .join(Categoria, Movimiento.categoria_id == Categoria.id, isouter=True)
        .join(TipoMovimiento, Movimiento.tipo_id == TipoMovimiento.id, isouter=True)
        .join(MetodoPago, Movimiento.metodo_pago_id == MetodoPago.id, isouter=True)
    )


def _aplicar_ordenacion(query, sort_by: Optional[str], sort_dir: Optional[str]):
    """Añade ordenación segura a la consulta, limitando los campos permitidos."""

    direcciones = {"asc": asc, "desc": desc}
    columnas_permitidas = {
        "fecha": Movimiento.fecha,
        "importe": Movimiento.importe,
        "categoria": Categoria.nombre,
        "tipo": TipoMovimiento.nombre,
        "metodo_pago": MetodoPago.nombre,
        "concepto": Movimiento.concepto,
    }
    if sort_by and sort_by in columnas_permitidas:
        orden = direcciones.get(sort_dir or "asc", asc)
        query = query.order_by(orden(columnas_permitidas[sort_by]))
    else:
        query = query.order_by(desc(Movimiento.fecha))
    return query


def _paginar(query, page: int, page_size: int):
    offset = (page - 1) * page_size
    return query.limit(page_size).offset(offset)


def _mapear_items(resultado) -> list[MovimientoListItem]:
    """Convierte filas del motor SQLAlchemy a pydantic list item."""

    items: list[MovimientoListItem] = []
    for row in resultado:
        movimiento: Movimiento = row.Movimiento
        items.append(
            MovimientoListItem(
                id=movimiento.id,
                fecha=movimiento.fecha,
                concepto=movimiento.concepto,
                importe=movimiento.importe,
                saldo=movimiento.saldo,
                tipo_id=movimiento.tipo_id,
                tipo_nombre=row.tipo_nombre,
                categoria_id=movimiento.categoria_id,
                categoria_nombre=row.categoria_nombre,
                categoria_es_fijo=row.categoria_es_fijo,
                metodo_pago_id=movimiento.metodo_pago_id,
                metodo_pago_nombre=row.metodo_pago_nombre,
                notas=movimiento.notas,
                mes_anio=movimiento.mes_anio,
            )
        )
    return items


def _calcular_agregados(db: Session, filtros: MovimientoFiltro) -> MovimientoAggregates:
    """Calcula totales de importes y recuentos siguiendo los filtros activos."""

    query_agregados = (
        select(
            func.count(Movimiento.id),
            func.coalesce(func.sum(Movimiento.importe), 0),
            func.coalesce(
                func.sum(case((Movimiento.importe < 0, Movimiento.importe), else_=0)), 0
            ),
            func.coalesce(
                func.sum(case((Movimiento.importe > 0, Movimiento.importe), else_=0)), 0
            ),
            func.min(Movimiento.fecha),
            func.max(Movimiento.fecha),
        )
        .join(Categoria, Movimiento.categoria_id == Categoria.id, isouter=True)
        .join(TipoMovimiento, Movimiento.tipo_id == TipoMovimiento.id, isouter=True)
        .join(MetodoPago, Movimiento.metodo_pago_id == MetodoPago.id, isouter=True)
    )
    query_agregados = aplicar_filtros(query_agregados, filtros)
    total_registros, total_importe, total_gastos, total_ingresos, fecha_min, fecha_max = db.execute(
        query_agregados
    ).one()

    promedio_mensual = None
    if fecha_min and fecha_max:
        meses = (fecha_max.year - fecha_min.year) * 12 + (fecha_max.month - fecha_min.month) + 1
        if meses > 0:
            promedio_mensual = float(total_importe) / meses

    return MovimientoAggregates(
        total_registros=total_registros,
        total_importe=float(total_importe or 0),
        total_gastos=float(total_gastos or 0),
        total_ingresos=float(total_ingresos or 0),
        promedio_mensual=promedio_mensual,
    )


def listar_movimientos(
    db: Session,
    filtros: Optional[MovimientoFiltro] = None,
    page: int = 1,
    page_size: int = 50,
    sort_by: Optional[str] = None,
    sort_dir: Optional[str] = None,
) -> MovimientoListResponse:
    """Obtiene movimientos aplicando filtros, paginación y agregados.

    Esta función centraliza la lógica del explorador de datos para permitir su
    reutilización en el listado principal y en el export.
    """

    filtros = filtros or MovimientoFiltro()
    base_query = _query_base_movimientos()
    filtrada = aplicar_filtros(base_query, filtros)
    ordenada = _aplicar_ordenacion(filtrada, sort_by, sort_dir)

    total_query = select(func.count(Movimiento.id)).select_from(
        aplicar_filtros(
            select(Movimiento.id)
            .join(Categoria, Movimiento.categoria_id == Categoria.id, isouter=True)
            .join(TipoMovimiento, Movimiento.tipo_id == TipoMovimiento.id, isouter=True)
            .join(MetodoPago, Movimiento.metodo_pago_id == MetodoPago.id, isouter=True),
            filtros,
        ).subquery()
    )
    total_items = db.scalar(total_query) or 0

    paginada = _paginar(ordenada, page, page_size)
    resultado = db.execute(paginada).all()
    items = _mapear_items(resultado)

    total_pages = max(1, (total_items + page_size - 1) // page_size) if total_items else 1
    agregados = _calcular_agregados(db, filtros)

    return MovimientoListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        aggregates=agregados,
    )


def exportar_movimientos(db: Session, filtros: MovimientoFiltro) -> Iterable[MovimientoListItem]:
    """Obtiene todos los movimientos filtrados sin paginación para exportar."""

    base = _query_base_movimientos()
    filtrada = aplicar_filtros(base, filtros)
    filtrada = _aplicar_ordenacion(filtrada, sort_by="fecha", sort_dir="desc")
    resultado = db.execute(filtrada).all()
    return _mapear_items(resultado)


def crear_movimiento(db: Session, datos: MovimientoCreate) -> Movimiento:
    """Crea un movimiento y aplica reglas automáticas."""

    movimiento = Movimiento(**datos.model_dump())
    movimiento.rellenar_campos_derivados()
    aplicar_reglas_movimiento(db, movimiento)
    db.add(movimiento)
    db.commit()
    db.refresh(movimiento)
    return movimiento


def actualizar_movimiento(db: Session, movimiento_id: int, datos: MovimientoUpdate) -> Movimiento:
    """Actualiza un movimiento existente."""

    movimiento = db.get(Movimiento, movimiento_id)
    if not movimiento:
        raise ValueError("Movimiento no encontrado")
    for campo, valor in datos.model_dump().items():
        setattr(movimiento, campo, valor)
    movimiento.rellenar_campos_derivados()
    aplicar_reglas_movimiento(db, movimiento)
    db.commit()
    db.refresh(movimiento)
    return movimiento


def actualizar_movimiento_inline(
    db: Session, movimiento_id: int, datos: MovimientoInlineUpdate
) -> MovimientoListItem:
    """Actualización parcial utilizada por las celdas editables del frontend."""

    movimiento = db.get(Movimiento, movimiento_id)
    if not movimiento:
        raise ValueError("Movimiento no encontrado")

    if datos.categoria_id is not None:
        categoria = db.get(Categoria, datos.categoria_id)
        if not categoria:
            raise ValueError("Categoría no encontrada")
        movimiento.categoria_id = datos.categoria_id
    if datos.metodo_pago_id is not None:
        metodo = db.get(MetodoPago, datos.metodo_pago_id)
        if not metodo:
            raise ValueError("Método de pago no encontrado")
        movimiento.metodo_pago_id = datos.metodo_pago_id
    if datos.notas is not None:
        movimiento.notas = datos.notas

    movimiento.rellenar_campos_derivados()
    db.commit()
    db.refresh(movimiento)

    enriched = db.execute(
        _query_base_movimientos().where(Movimiento.id == movimiento_id)
    ).one()
    return _mapear_items([enriched])[0]


def borrar_movimiento(db: Session, movimiento_id: int) -> None:
    """Elimina un movimiento."""

    movimiento = db.get(Movimiento, movimiento_id)
    if movimiento:
        db.delete(movimiento)
        db.commit()
