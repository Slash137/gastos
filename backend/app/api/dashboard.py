"""Endpoints de analítica y KPIs."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models import Categoria, Movimiento
from backend.app.schemas.dashboard import BalanceAnual, DashboardResponse, DistribucionCategoria, KPIs, SerieMensual

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _calcular_kpis(db: Session, serie_mensual: list[SerieMensual]) -> KPIs:
    total_ingresos = db.query(func.coalesce(func.sum(case((Movimiento.importe > 0, Movimiento.importe), else_=0))),).scalar() or 0
    total_gastos = db.query(func.coalesce(func.sum(case((Movimiento.importe < 0, Movimiento.importe), else_=0))),).scalar() or 0
    balance_neto = total_ingresos + total_gastos

    medias = [p.saldo for p in serie_mensual]
    media_mensual = sum(medias) / len(medias) if medias else 0
    variacion_mensual = 0
    if len(medias) >= 2:
        variacion_mensual = medias[-1] - medias[-2]

    # Regresión lineal simple sobre el índice temporal
    if len(medias) >= 2:
        x_vals = list(range(len(medias)))
        x_mean = sum(x_vals) / len(x_vals)
        y_mean = sum(medias) / len(medias)
        numerador = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_vals, medias))
        denominador = sum((x - x_mean) ** 2 for x in x_vals) or 1
        slope = numerador / denominador
    else:
        slope = 0
    saldo_actual = medias[-1] if medias else 0
    proyeccion_30d = saldo_actual + slope
    proyeccion_60d = saldo_actual + slope * 2

    return KPIs(
        total_ingresos=total_ingresos,
        total_gastos=abs(total_gastos),
        balance_neto=balance_neto,
        media_mensual=media_mensual,
        variacion_mensual=variacion_mensual,
        proyeccion_30d=proyeccion_30d,
        proyeccion_60d=proyeccion_60d,
    )


def _serie_mensual(db: Session) -> list[SerieMensual]:
    query = (
        db.query(Movimiento.mes_anio, func.sum(Movimiento.importe).label("total"))
        .group_by(Movimiento.mes_anio)
        .order_by(Movimiento.mes_anio)
    )
    totales = query.all()
    saldo_acumulado = 0
    serie: list[SerieMensual] = []
    for mes_anio, total in totales:
        saldo_acumulado += float(total or 0)
        serie.append(SerieMensual(mes_anio=mes_anio, saldo=saldo_acumulado))
    return serie


def _distribucion_categoria(db: Session) -> list[DistribucionCategoria]:
    query = (
        db.query(Categoria.nombre, func.sum(Movimiento.importe).label("total"))
        .join(Movimiento, Movimiento.categoria_id == Categoria.id)
        .group_by(Categoria.nombre)
    )
    return [DistribucionCategoria(categoria=nombre, total=float(total or 0)) for nombre, total in query.all()]


def _balance_anual(db: Session) -> list[BalanceAnual]:
    query = (
        db.query(
            Movimiento.anio,
            func.sum(case((Movimiento.importe < 0, Movimiento.importe), else_=0)).label("gastos"),
            func.sum(case((Movimiento.importe > 0, Movimiento.importe), else_=0)).label("ingresos"),
        )
        .group_by(Movimiento.anio)
        .order_by(Movimiento.anio)
    )
    return [
        BalanceAnual(anio=anio, total_gastos=abs(gastos or 0), total_ingresos=float(ingresos or 0))
        for anio, gastos, ingresos in query.all()
    ]


@router.get("", response_model=DashboardResponse)
def obtener_dashboard(db: Session = Depends(get_db)) -> DashboardResponse:
    """Calcula KPIs y series para el panel analítico."""

    serie = _serie_mensual(db)
    return DashboardResponse(
        kpis=_calcular_kpis(db, serie),
        serie_mensual=serie,
        distribucion_categoria=_distribucion_categoria(db),
        balance_anual=_balance_anual(db),
    )
