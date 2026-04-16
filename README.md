# FoodTruck SaaS — Contexto completo del proyecto (Sprint 1)

Plataforma SaaS **web mobile-first** para pequeños negocios gastronómicos: food trucks, cafeterías, dark kitchens y locales pequeños con una o más sucursales.

---

## 1) ¿De qué se trata este proyecto?

Este repositorio contiene la **base fundacional** de un producto SaaS que busca resolver operación gastronómica diaria de forma simple desde celular, sin perder capacidad de escalar a operación multi-sucursal y multi-tenant.

La idea no es construir todo en el primer sprint, sino construir una base sólida que evite reescrituras costosas en próximos sprints.

---

## 2) ¿Hacia dónde va el producto?

La visión de producto evoluciona por iteraciones:

1. **Sprint 1 (actual):** fundación técnica + autenticación + dominio multi-tenant/multi-sucursal.
2. **Siguientes sprints:** catálogo de productos, pedidos, stock, métricas, comprobantes e infraestructura más robusta.

Objetivo estratégico: pasar de operación básica a una plataforma profesional para negocios gastronómicos emergentes.

---

## 3) Principios de arquitectura (desde día 1)

- **Multi-tenant por diseño:** aislamiento lógico por negocio (tenant).
- **Multi-sucursal por dominio:** contexto branch desde modelos y casos de uso.
- **Autorización en backend:** el frontend refleja permisos, no decide seguridad.
- **Monolito modular:** velocidad de entrega + mantenibilidad.
- **Mobile-first en frontend:** operación principal desde pantallas pequeñas.
- **Cloud-native en GCP:** preparada para Cloud Run + Cloud SQL + Secret Manager.

---

## 4) Alcance exacto de Sprint 1 (lo que SÍ construimos)

- Frontend base con **Next.js + TypeScript + Tailwind**.
- Backend base con **FastAPI + PostgreSQL + SQLAlchemy + Alembic**.
- Autenticación funcional con JWT.
- Contexto multi-tenant y multi-sucursal.
- Roles base:
  - `seller`
  - `branch_admin`
  - `tenant_admin`
  - `platform_admin`
- Rutas protegidas por autenticación y rol.
- CRUD mínimo de:
  - `tenants`
  - `branches`
  - `users`
  - `roles` (solo lectura)
- Migración inicial + seed demo.
- Docker + docker-compose para ejecución local.
- Documentación mínima de arquitectura y preparación para GCP.

---

## 5) Qué NO construimos en Sprint 1 (límite de diseño)

Este punto es crítico para mantener el sprint sano.

No se implementa aún:
- pedidos,
- order items,
- stock,
- dashboard real,
- reportes,
- comprobantes/PDF,
- billing SaaS,
- permisos granulares avanzados,
- integraciones externas complejas,
- paneles y módulos prematuros.

> Regla de oro del Sprint 1: construir base estable, no sobre-ingeniería.

---

## 6) Estado esperado al terminar Sprint 1

Al cerrar este sprint, el sistema queda en esta situación:

- puedes autenticarte,
- puedes distinguir tenants y sucursales,
- puedes gestionar usuarios básicos,
- puedes proteger acceso por rol,
- tienes entorno local y base lista para staging,
- el proyecto está preparado para crecer sin reescritura.

---

## 7) Estructura del repositorio

```txt
apps/
  api/
  web/
docs/
scripts/
packages/
```

- `apps/api`: backend FastAPI modular.
- `apps/web`: frontend Next.js mobile-first.
- `docs`: arquitectura y guía inicial GCP.
- `scripts`: utilidades de arranque.
- `packages/shared-types`: reservado para tipados compartidos futuros.

---

## 8) Backend (detalle)

Módulos implementados:
- `auth`
- `tenants`
- `branches`
- `users`
- `roles`

Endpoints principales:
- `GET /health`
- `GET /ready`
- `POST /auth/login`
- `GET /auth/me`
- `GET /roles`
- `GET/POST/GET by id/PATCH /tenants`
- `GET/POST/GET by id/PATCH /branches`
- `GET/POST/GET by id/PATCH /users`

### Entidades mínimas
- `tenants`
- `branches`
- `roles`
- `users`
- `user_branch_assignments`

### Reglas relevantes
- Entidades tenant-scoped incluyen `tenant_id`.
- Contexto de tenant se controla en backend según usuario autenticado.
- El frontend no define autorización.

---

## 9) Frontend (detalle)

Rutas base:
- `/login`
- `/seller`
- `/branch-admin`
- `/tenant-admin`
- `/platform-admin`

Cada vista protegida valida sesión/token y consulta `/auth/me` para validar rol.

---

## 10) Cómo correr localmente

### Configuración inicial de variables

```bash
cp .env.example .env
```

> `.env` es local y no se versiona. Nunca subas secretos reales al repositorio.

### Levantar stack base (sin demo seed)

```bash
docker compose up --build
```

Servicios:
- API: http://localhost:8000
- Web: http://localhost:3000

### Perfil de desarrollo con seed demo explícito

```bash
docker compose --profile dev up --build
```

Este perfil ejecuta `api-seed-demo` para poblar usuarios demo.

#### Credenciales demo (solo perfil `dev`)

Password para todos: `Pass1234!`

- `seller@demo.com`
- `branch@demo.com`
- `tenant@demo.com`
- `platform@demo.com`

### Migración + seed manual (backend)

```bash
cd apps/api
alembic upgrade head
python scripts_seed.py
uvicorn app.main:app --reload
```

---

## 11) Preparación para deploy (GCP)

Objetivo inicial (sin complejidad excesiva aún):
- Cloud Run para `api` y `web`.
- Cloud SQL PostgreSQL para datos.
- Secret Manager para `DATABASE_URL` y `JWT_SECRET_KEY`.

### Checklist de seguridad para despliegue

- [ ] Definir `APP_ENV=prod` (o equivalente no-dev) en runtime.
- [ ] Configurar `DATABASE_URL` desde Secret Manager/variables seguras, nunca hardcodeado.
- [ ] Configurar `JWT_SECRET_KEY` aleatorio y único (mínimo 32 caracteres).
- [ ] Verificar que `.env` no se comitea y que solo existe `.env.example` versionado.
- [ ] No ejecutar `api-seed-demo` en staging/producción (perfil solo desarrollo).
- [ ] Rotar secretos si hubo exposición accidental en historial o logs.

Más detalle en:
- `docs/architecture.md`
- `docs/gcp.md`

---

## 12) Filosofía de evolución

Este proyecto evoluciona por sprints cortos con foco en valor real:

- construir lo necesario,
- evitar tablas y abstracciones prematuras,
- mantener código simple y extensible,
- validar rápido con negocio,
- preparar el terreno para módulos operativos (productos/pedidos/stock) en próximas iteraciones.

Si en Sprint 2 se necesita backlog técnico detallado (historias + tareas + criterios de aceptación), se puede desglosar a partir de esta base.
