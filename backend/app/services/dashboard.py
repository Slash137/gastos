"""Servicios de cálculo para el dashboard analítico.

Toda la lógica intensiva de agregación se concentra aquí para mantener los
endpoints ligeros y reutilizar el filtrado existente de movimientos.
"""

from __future__ import annotations

from statistics import mean
from typing import Sequence

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from backend.app.models import Categoria, Movimiento
from backend.app.schemas.dashboard import (
    DashboardCategoryPoint,
    DashboardFiltro,
    DashboardMonthlyPoint,
    DashboardSummary,
    DashboardYearPoint,
)
from backend.app.schemas.movimientos import MovimientoFiltro
from backend.app.services.movimientos import aplicar_filtros


def _convertir_a_filtro_movimiento(filtros: DashboardFiltro) -> MovimientoFiltro:
    """Adapta los filtros de dashboard al modelo de movimientos.

    Esto permite reutilizar la lógica de `aplicar_filtros` para no divergir en
    la interpretación de parámetros como fechas, categorías o banderas de
    gastos fijos/variables.
    """

    return MovimientoFiltro(
        fecha_desde=filtros.fecha_desde,
        fecha_hasta=filtros.fecha_hasta,
        categoria_ids=filtros.categoria_ids,
        tipo_ids=filtros.tipo_ids,
        metodo_pago_ids=filtros.metodo_pago_ids,
        solo_gastos_fijos=filtros.solo_gastos_fijos,
        solo_gastos_variables=filtros.solo_gastos_variables,
    )


def _consulta_filtrada(filtros: DashboardFiltro):
    """Construye una consulta base con joins preparados para filtrar."""

    base = select(Movimiento).join(Categoria, Movimiento.categoria_id == Categoria.id, isouter=True)
    return aplicar_filtros(base, _convertir_a_filtro_movimiento(filtros))


def _serie_mensual(
    db: Session, filtros: DashboardFiltro
) -> Sequence[tuple[str, float, float, float]]:
    """Agrupa por mes para obtener gastos, ingresos y balance neto."""

    consulta = _consulta_filtrada(filtros).subquery()
    query = (
        select(
            consulta.c.mes_anio,
            func.sum(case((consulta.c.importe < 0, consulta.c.importe), else_=0)).label("total_gastos"),
            func.sum(case((consulta.c.importe > 0, consulta.c.importe), else_=0)).label("total_ingresos"),
            func.sum(consulta.c.importe).label("balance"),
        )
        .group_by(consulta.c.mes_anio, consulta.c.anio, consulta.c.mes)
        .order_by(consulta.c.anio, consulta.c.mes)
    )
    return db.execute(query).all()


def _totales_base(db: Session, filtros: DashboardFiltro):
    """Calcula los totales simples reutilizados por varios cálculos."""

    consulta = _consulta_filtrada(filtros).subquery()
    query = select(
        func.coalesce(func.sum(case((consulta.c.importe < 0, consulta.c.importe), else_=0)), 0).label(
            "total_gastos"
        ),
        func.coalesce(func.sum(case((consulta.c.importe > 0, consulta.c.importe), else_=0)), 0).label(
            "total_ingresos"
        ),
        func.coalesce(func.sum(consulta.c.importe), 0).label("balance"),
    )
    return db.execute(query).one()


def obtener_resumen(db: Session, filtros: DashboardFiltro) -> DashboardSummary:
    """Devuelve KPIs agregados del dashboard."""

    totales = _totales_base(db, filtros)
    total_gastos = float(totales.total_gastos or 0)
    total_ingresos = float(totales.total_ingresos or 0)
    balance_neto = float(totales.balance or 0)

    serie = _serie_mensual(db, filtros)

    gastos_por_mes = [abs(float(fila.total_gastos or 0)) for fila in serie]
    gasto_medio_mensual = mean(gastos_por_mes) if gastos_por_mes else 0.0

    variacion = None
    if len(gastos_por_mes) >= 2 and gastos_por_mes[-2] != 0:
        variacion = ((gastos_por_mes[-1] - gastos_por_mes[-2]) / gastos_por_mes[-2]) * 100

    balances_mensuales = [float(fila.balance or 0) for fila in serie]
    promedio_balance = mean(balances_mensuales) if balances_mensuales else None

    proyeccion_30 = None
    proyeccion_60 = None
    if promedio_balance is not None:
        promedio_diario = promedio_balance / 30
        proyeccion_30 = balance_neto + promedio_diario * 30
        proyeccion_60 = balance_neto + promedio_diario * 60

    return DashboardSummary(
        total_gastos=abs(total_gastos),
        total_ingresos=total_ingresos,
        balance_neto=balance_neto,
        gasto_medio_mensual=gasto_medio_mensual,
        variacion_mensual_porcentaje=variacion,
        proyeccion_saldo_30d=proyeccion_30,
        proyeccion_saldo_60d=proyeccion_60,
    )


def obtener_serie_mensual(db: Session, filtros: DashboardFiltro) -> list[DashboardMonthlyPoint]:
    """Serie mensual ordenada ascendente para gráficos de evolución."""

    serie = _serie_mensual(db, filtros)
    puntos: list[DashboardMonthlyPoint] = []
    for fila in serie:
        puntos.append(
            DashboardMonthlyPoint(
                mes_anio=fila.mes_anio,
                total_gastos=abs(float(fila.total_gastos or 0)),
                total_ingresos=float(fila.total_ingresos or 0),
                balance_neto=float(fila.balance or 0),
            )
        )
    return puntos


def obtener_por_categoria(db: Session, filtros: DashboardFiltro) -> list[DashboardCategoryPoint]:
    """Distribución de importes por categoría incluyendo valores sin categoría."""

    filtro_mov = _convertir_a_filtro_movimiento(filtros)
    base_sumatoria = (
        select(
            Movimiento.categoria_id,
            Categoria.nombre.label("categoria_nombre"),
            func.sum(Movimiento.importe).label("total_importe"),
            func.sum(case((Movimiento.importe < 0, Movimiento.importe), else_=0)).label("total_gastos"),
            func.sum(case((Movimiento.importe > 0, Movimiento.importe), else_=0)).label("total_ingresos"),
        )
        .select_from(Movimiento)
        .join(Categoria, Movimiento.categoria_id == Categoria.id, isouter=True)
    )
    base_sumatoria = aplicar_filtros(base_sumatoria, filtro_mov)
    base_sumatoria = base_sumatoria.group_by(Movimiento.categoria_id, Categoria.nombre)

    consulta_total = aplicar_filtros(
        select(Movimiento).join(Categoria, Movimiento.categoria_id == Categoria.id, isouter=True),
        filtro_mov,
    ).subquery()
    total_gastos_periodo_query = select(
        func.coalesce(func.sum(case((consulta_total.c.importe < 0, consulta_total.c.importe), else_=0)), 0)
    )
    total_gastos_periodo = abs(float(db.scalar(total_gastos_periodo_query) or 0))

    puntos: list[DashboardCategoryPoint] = []
    for categoria_id, categoria_nombre, total_importe, total_gastos, total_ingresos in db.execute(base_sumatoria):
        total_gastos_abs = abs(float(total_gastos or 0))
        porcentaje = 0.0
        if total_gastos_periodo:
            porcentaje = (total_gastos_abs / total_gastos_periodo) * 100
        puntos.append(
            DashboardCategoryPoint(
                categoria_id=categoria_id,
                categoria_nombre=categoria_nombre or "Sin categoría",
                total_importe=float(total_importe or 0),
                total_gastos=total_gastos_abs,
                total_ingresos=float(total_ingresos or 0),
                porcentaje_sobre_total=porcentaje,
            )
        )
    return puntos


def obtener_por_anio(db: Session, filtros: DashboardFiltro) -> list[DashboardYearPoint]:
    """Agregación anual para gráficas de comparación de años."""

    filtro_mov = _convertir_a_filtro_movimiento(filtros)
    base = (
        select(
            Movimiento.anio,
            func.sum(case((Movimiento.importe < 0, Movimiento.importe), else_=0)).label("total_gastos"),
            func.sum(case((Movimiento.importe > 0, Movimiento.importe), else_=0)).label("total_ingresos"),
            func.sum(Movimiento.importe).label("balance"),
        )
        .select_from(Movimiento)
        .join(Categoria, Movimiento.categoria_id == Categoria.id, isouter=True)
    )
    base = aplicar_filtros(base, filtro_mov)
    base = base.group_by(Movimiento.anio).order_by(Movimiento.anio)

    puntos: list[DashboardYearPoint] = []
    for anio, total_gastos, total_ingresos, balance in db.execute(base):
        puntos.append(
            DashboardYearPoint(
                anio=anio,
                total_gastos=abs(float(total_gastos or 0)),
                total_ingresos=float(total_ingresos or 0),
                balance_neto=float(balance or 0),
            )
        )
    return puntos
