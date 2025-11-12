# Instrucciones para colaboradores del proyecto "gastos"

## Alcance
Estas instrucciones se aplican a todo el repositorio salvo que un subdirectorio contenga su propio `AGENTS.md`.

## Estilo general
- Mantén el diseño y estilo existentes; cualquier adición debe respetar un enfoque responsive y mobile-first inspirado en Google/StelOrder.
- Evita eliminar funcionalidades salvo que el solicitante lo indique expresamente.
- Comenta el código explicando su objetivo y las decisiones de diseño relevantes.
- Aporta soluciones completas y mantenibles; no desactives validaciones ni funcionalidades como atajo.

## Backend
- Utiliza FastAPI como framework principal para los servicios web.
- Organiza el código backend dentro del directorio `backend/` usando una estructura modular (`app/`, `routers/`, `schemas/`, etc.).
- Acompaña cada módulo con docstrings o comentarios que describan la lógica clave.

## Frontend
- Sitúa todo el código del frontend en `frontend/` y sigue un enfoque mobile-first.
- Conserva coherencia con las páginas `/maquinas/` y `/clientes/` que servirán de referencia visual en futuras implementaciones.

## Pruebas y calidad
- Cuando añadas funcionalidades, incluye pruebas automatizadas cuando sea factible.
- Documenta en los mensajes de commit y PR los comandos de verificación ejecutados.

## Documentación
- Mantén actualizados los archivos de documentación cuando introduzcas nuevos módulos o flujos de trabajo relevantes.

