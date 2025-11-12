# Roadmap del Proyecto de Gestión de Gastos

> **Objetivo general:** construir una aplicación web local que permita importar extractos bancarios en formato CSV, gestionarlos en una base de datos estructurada y ofrecer visualizaciones, filtros y análisis avanzados sobre los movimientos de una cuenta doméstica.

## 1. Visión del producto
- Centralizar en un único panel todos los gastos e ingresos de la vivienda.
- Facilitar la importación de extractos bancarios con validación y enriquecimiento de datos.
- Disponer de filtros y vistas personalizadas por periodo, categoría, tipo de movimiento y método de pago.
- Proporcionar analítica visual y seguimiento del saldo proyectado a corto y medio plazo.
- Permitir la futura ampliación hacia módulos "nice to have" como contratos o recordatorios.

## 2. Entregables principales
1. **Backend FastAPI** con endpoints REST para importar CSV, gestionar movimientos y exponer datos agregados.
2. **Base de datos relacional** (SQLite en desarrollo, PostgreSQL en producción) con esquema alineado al modelo ER proporcionado.
3. **Frontend React** responsive y mobile-first que replique el estilo referencial existente (Google/StelOrder).
4. **Módulo de análisis** con gráficas interactivas, tablas filtrables y proyecciones de saldo.
5. **Automatizaciones** de pruebas, linting y despliegue local mediante Docker Compose.

## 3. Fases del roadmap
### Fase 0 · Preparación (Semana 1)
- Revisar el modelo ER y definir claramente las entidades (Movimientos, Categorías, Tipos, Métodos de pago, Usuarios).
- Configurar repositorios, entorno de desarrollo, control de versiones y CI básica.
- Definir convenciones de estilo para backend y frontend.

### Fase 1 · Ingesta de datos (Semanas 2-3)
- Implementar un servicio de importación CSV usando Pandas con validaciones (formato de fecha, números decimales, separación de columnas, categorías existentes).
- Crear API para carga manual y automática de ficheros.
- Registrar incidencias de importación y trazabilidad por fila.

### Fase 2 · Backend funcional (Semanas 3-5)
- Exponer endpoints CRUD para movimientos, categorías, tipos y notas.
- Construir consultas parametrizadas para filtros por rango de fechas, importes, categorías y tipo de transacción.
- Implementar autenticación básica (JWT) si se habilita multiusuario.
- Desplegar pruebas unitarias e integración con pytest y coverage.

### Fase 3 · Frontend básico (Semanas 4-6)
- Crear layout principal responsive siguiendo el estilo de las páginas `/maquinas/` y `/clientes/` del proyecto.
- Desarrollar vistas: tablero mensual, listado completo de movimientos, detalle de movimiento y configuración de categorías.
- Integrar React Query para el consumo de la API y caching.
- Añadir formularios de filtrado avanzados con validaciones en cliente.

### Fase 4 · Analítica y visualización (Semanas 6-8)
- Implementar gráficas con Recharts o ECharts para evolución de saldo, distribución por categorías y comparativas mensuales.
- Añadir tablas dinámicas (TanStack Table / Ag-Grid) con ordenación, filtrado y exportación.
- Calcular KPIs: gasto medio mensual, variación intermensual, proyección de saldo a 30/60 días.

### Fase 5 · Pulido y despliegue local (Semanas 8-9)
- Incorporar control de errores y mensajes accesibles en la UI.
- Configurar Docker Compose con servicios para backend, base de datos y frontend.
- Documentar procedimientos de importación, backup y restauración.
- Ejecutar pruebas end-to-end básicas (Playwright/Cypress) en la vista crítica de movimientos.

### Fase 6 · Ampliaciones futuras (a demanda)
- Módulo de contratos y recordatorios de vencimientos.
- Integración con APIs bancarias para sincronización automática.
- Gestión multiusuario con roles y permisos.
- Notificaciones (email/push) para alertas de presupuesto.

## 4. Hitos y métricas de éxito
- **Hito 1:** Importación CSV validada, con más del 95 % de registros aceptados sin error.
- **Hito 2:** Backend cubierto al 80 % por pruebas unitarias y de integración.
- **Hito 3:** Frontend responsive con tiempos de carga menores a 2 s en dispositivos móviles de gama media.
- **Hito 4:** Panel analítico que muestre al menos 3 visualizaciones relevantes con datos reales.
- **Hito 5:** Entorno Docker Compose funcionando con un solo comando `docker compose up`.

## 5. Riesgos y mitigaciones
- **Calidad del CSV:** archivos mal formados o con separadores inconsistentes. → Añadir validaciones estrictas y guías para exportación.
- **Escalabilidad futura:** comenzar en SQLite puede limitar concurrencia. → Definir migraciones y abstracción de ORM para cambiar a PostgreSQL sin fricción.
- **Adopción de usuarios:** interfaz compleja. → Mantener diseño minimalista y coherente con referencias existentes.
- **Seguridad local:** posible exposición de datos sensibles al compartir dispositivo. → Ofrecer cifrado de base de datos y autenticación opcional.

## 6. Próximos pasos inmediatos
1. Priorizar y cerrar la definición del modelo de datos definitivo.
2. Generar historias de usuario y criterios de aceptación para cada vista.
3. Configurar el repositorio con plantillas de issues, PRs y pipelines mínimos.

## 7. Requisitos de entorno
- **Versión de Python:** 3.9.6 (usa `pyenv` o la herramienta de tu preferencia para fijar la versión exacta).
- **Instalación de dependencias:** ejecuta `pip install -e '.[dev]'` dentro de un entorno virtual basado en Python 3.9.6.
- **Ejecución de pruebas rápidas:** `pytest backend/tests/test_health.py` valida la disponibilidad del endpoint de salud configurado en FastAPI.

## 8. Referencias internas
- `Modelo_ER.jpg`: base conceptual del esquema relacional a depurar.
- `contratos.jpg`: funcionalidad futura opcional que puede integrarse tras la Fase 6.

> Este roadmap servirá como guía viva. Se recomienda revisarlo al final de cada fase para ajustar prioridades según feedback y carga de trabajo disponible.
