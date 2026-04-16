# AGENTS.md — Reglas obligatorias para Codex (scope: todo el repo)

Estas reglas son de cumplimiento estricto para cualquier cambio en este repositorio.
Objetivo: evitar regresiones de arquitectura, seguridad, calidad y operabilidad.

## 0) Principio rector
- **No se aprueba código “solo porque funciona”.**
- Cada cambio debe justificar impacto en: seguridad, mantenibilidad, testing y operación.

## 1) Arquitectura y límites de capas
- Mantener separación de responsabilidades:
  - `api/routes`: solo HTTP (parseo, status code, wiring de dependencias).
  - `services`: casos de uso y reglas de negocio.
  - `repositories`: acceso a datos; sin reglas de negocio de autorización.
  - `schemas`: contratos de entrada/salida.
- Prohibido meter lógica de negocio compleja en rutas.
- Prohibido mezclar autorización ad-hoc duplicada en múltiples endpoints.
- Si una regla aplica a varios módulos, debe centralizarse (servicio/policy).

## 2) Reglas de seguridad (obligatorias)
- Todo endpoint no público debe requerir autenticación.
- Toda operación sobre recursos tenant/branch-scoped debe validar `scope` explícito.
- **Nunca** permitir asignación libre de roles desde payload sin policy de actor.
- Implementar y mantener matriz de autorización actor/recurso/acción.
- Prohibido confiar en datos del cliente para autorización (headers o payload sin validar).
- Secretos:
  - Prohibido commitear secretos reales.
  - Prohibido usar defaults inseguros en entornos no-dev.
  - Startup debe fallar si falta secreto crítico o es débil.
- Login debe tener mitigación anti abuso (rate limiting o lockout/backoff).
- No exponer datos sensibles en logs (tokens, passwords, hashes completos, PII innecesaria).

## 3) FastAPI y contratos de API
- Definir `response_model` en endpoints.
- Estandarizar errores (no mezclar mensajes/formatos arbitrarios).
- Usar status code correcto (`401/403/404/409/422/500`).
- Endpoints de listado deben soportar paginación (evitar `all()` sin límites en producción).
- `/ready` debe validar dependencias críticas (DB y/o servicios necesarios).

## 4) Persistencia y transacciones
- Evitar repositorio genérico para casos con reglas de negocio complejas.
- Operaciones de escritura críticas deben manejar transacción explícita y rollback ante error.
- Errores de integridad (`unique`, FK, etc.) deben mapearse a errores de dominio/API (409/422), no 500 genérico.
- Toda relación many-to-many debe tener constraints/índices adecuados.
- Mantener coherencia tenant/branch/user con validaciones y/o constraints.

## 5) Rendimiento y escalabilidad
- Evitar N+1 y queries redundantes por request.
- Evitar cargar colecciones completas sin límites.
- Definir timeouts en integraciones externas.
- Si se usa caché, definir invalidación explícita.

## 6) Testing mínimo obligatorio por cambio
Para aceptar un PR, el cambio debe incluir pruebas proporcionales al riesgo:
- Seguridad/autorización: tests de integración actor/recurso/acción.
- Contratos API: tests de status codes y shape de respuesta/errores.
- Persistencia: tests de integridad y migraciones cuando aplique.
- Bugfix: al menos 1 test que falle antes y pase después.

## 7) CI/CD y calidad
- No mergear si falla cualquiera de:
  - lint
  - type checks
  - tests
  - migraciones
- No desplegar con configuración de desarrollo (`--reload`, debug abierto, secretos demo).

## 8) Observabilidad y operación
- Logs estructurados con contexto mínimo: `request_id`, actor, tenant_id, branch_id (si aplica).
- Registrar eventos relevantes de seguridad (login éxito/fallo, denegaciones 403).
- Healthchecks:
  - `/health`: proceso vivo.
  - `/ready`: dependencias listas.

## 9) Definición de Done (DoD)
Un cambio se considera terminado solo si:
1. Cumple reglas de seguridad y autorización del dominio afectado.
2. Incluye/actualiza tests necesarios.
3. No introduce deuda técnica crítica nueva.
4. Documenta decisiones y trade-offs no triviales.
5. Pasa checks automáticos.

## 10) Reglas de revisión de PR para Codex
En cada PR, Codex debe incluir obligatoriamente:
- Riesgos del cambio.
- Controles de seguridad aplicados.
- Estrategia de rollback si rompe en producción.
- Evidencia de tests/checks ejecutados.

## 11) Patrones prohibidos (lista corta)
- `role_id` del payload aplicado sin validación de policy.
- Filtrar solo por tenant cuando el recurso requiere scope de branch.
- `commit()` directo sin estrategia de rollback/mapeo de errores.
- Endpoints de listado sin paginación.
- Secrets hardcodeados para entornos reales.
