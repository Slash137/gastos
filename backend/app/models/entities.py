"""Definición de modelos ORM alineados con el ER del proyecto."""

from __future__ import annotations

from datetime import date
from enum import Enum

from sqlalchemy import Boolean, CheckConstraint, Date, Enum as SqlEnum, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base


class CampoObjetivo(str, Enum):
    """Campos sobre los que puede aplicarse una regla de autocategorización."""

    concepto = "concepto"
    notas = "notas"


class TipoMatch(str, Enum):
    """Tipo de coincidencia. De momento solo se contempla "contains"."""

    contains = "contains"


class TipoMovimiento(Base):
    """Tipo de movimiento: 1 gasto, 2 ingreso."""

    __tablename__ = "tipos_movimiento"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    movimientos: Mapped[list[Movimiento]] = relationship("Movimiento", back_populates="tipo")


class Categoria(Base):
    """Categorías de gasto/ingreso."""

    __tablename__ = "categorias"
    __table_args__ = (UniqueConstraint("nombre", name="uq_categoria_nombre"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    es_fijo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    movimientos: Mapped[list[Movimiento]] = relationship("Movimiento", back_populates="categoria")
    reglas: Mapped[list[ReglaAutoCategoria]] = relationship("ReglaAutoCategoria", back_populates="categoria")


class MetodoPago(Base):
    """Métodos de pago (efectivo, tarjeta, transferencia…)."""

    __tablename__ = "metodos_pago"
    __table_args__ = (UniqueConstraint("nombre", name="uq_metodo_pago_nombre"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    movimientos: Mapped[list[Movimiento]] = relationship("Movimiento", back_populates="metodo_pago")


class ReglaAutoCategoria(Base):
    """Reglas que permiten asignar categorías automáticamente."""

    __tablename__ = "reglas_auto_categoria"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pattern: Mapped[str] = mapped_column(String(255), nullable=False)
    campo_objetivo: Mapped[CampoObjetivo] = mapped_column(SqlEnum(CampoObjetivo), nullable=False)
    tipo_match: Mapped[TipoMatch] = mapped_column(SqlEnum(TipoMatch), nullable=False, default=TipoMatch.contains)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id", ondelete="CASCADE"), nullable=False)

    categoria: Mapped[Categoria] = relationship("Categoria", back_populates="reglas")


class Movimiento(Base):
    """Movimientos económicos con campos derivados para facilitar reporting."""

    __tablename__ = "movimientos"
    __table_args__ = (
        CheckConstraint("importe != 0", name="ck_importe_no_cero"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    concepto: Mapped[str] = mapped_column(String(255), nullable=False)
    importe: Mapped[float] = mapped_column(Float, nullable=False)
    saldo: Mapped[float | None] = mapped_column(Float, nullable=True)
    notas: Mapped[str | None] = mapped_column(String(500), nullable=True)

    tipo_id: Mapped[int] = mapped_column(ForeignKey("tipos_movimiento.id"), nullable=False)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"), nullable=False)
    metodo_pago_id: Mapped[int] = mapped_column(ForeignKey("metodos_pago.id"), nullable=False)

    anio: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    mes_anio: Mapped[str] = mapped_column(String(7), nullable=False, index=True)

    tipo: Mapped[TipoMovimiento] = relationship("TipoMovimiento", back_populates="movimientos")
    categoria: Mapped[Categoria] = relationship("Categoria", back_populates="movimientos")
    metodo_pago: Mapped[MetodoPago] = relationship("MetodoPago", back_populates="movimientos")

    def rellenar_campos_derivados(self) -> None:
        """Calcula valores derivados a partir de la fecha."""

        self.anio = self.fecha.year
        self.mes = self.fecha.month
        self.mes_anio = f"{self.fecha.year:04d}-{self.fecha.month:02d}"
