"""Módulo de seguridad.

Actualmente no se requiere autenticación compleja pero este archivo sirve de
punto central para futuras utilidades (hashing, JWT, permisos)."""

import hashlib


def hash_text(text: str) -> str:
    """Devuelve un hash SHA256 sencillo para casos de prueba."""

    return hashlib.sha256(text.encode("utf-8")).hexdigest()
