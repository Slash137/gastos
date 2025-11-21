"""Endpoints para categorías."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models import Categoria
from backend.app.schemas.categorias import CategoriaCreate, CategoriaRead, CategoriaUpdate

router = APIRouter(prefix="/categorias", tags=["categorias"])


def _obtener_categoria(db: Session, categoria_id: int) -> Categoria:
    categoria = db.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada")
    return categoria


@router.get("", response_model=list[CategoriaRead])
def listar_categorias(db: Session = Depends(get_db)):
    """Lista todas las categorías."""

    return db.query(Categoria).all()


@router.post("", response_model=CategoriaRead, status_code=status.HTTP_201_CREATED)
def crear_categoria(datos: CategoriaCreate, db: Session = Depends(get_db)):
    """Crea una nueva categoría."""

    categoria = Categoria(**datos.model_dump())
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


@router.put("/{categoria_id}", response_model=CategoriaRead)
def actualizar_categoria(categoria_id: int, datos: CategoriaUpdate, db: Session = Depends(get_db)):
    """Actualiza una categoría existente."""

    categoria = _obtener_categoria(db, categoria_id)
    for campo, valor in datos.model_dump().items():
        setattr(categoria, campo, valor)
    db.commit()
    db.refresh(categoria)
    return categoria


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    """Elimina una categoría."""

    categoria = _obtener_categoria(db, categoria_id)
    db.delete(categoria)
    db.commit()
