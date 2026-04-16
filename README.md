# FoodTruck SaaS — Sprint 1

Plataforma SaaS web mobile-first para food trucks, cafeterías y pequeños locales gastronómicos.

## Propósito

Este Sprint 1 implementa la fundación técnica del producto con arquitectura preparada para evolución sin reescrituras mayores.

## Alcance Sprint 1

- Frontend base con Next.js + TypeScript + Tailwind.
- Backend base con FastAPI + PostgreSQL + SQLAlchemy + Alembic.
- Autenticación funcional con JWT.
- Multi-tenant y multi-sucursal desde el modelo de datos.
- Roles base: `seller`, `branch_admin`, `tenant_admin`, `platform_admin`.
- Rutas protegidas por autenticación/rol.
- CRUD mínimo de tenants, branches y users.
- Lectura de roles.
- Seed demo con 1 tenant, 2 branches, 4 users.
- Docker y docker-compose para ejecución local.
- Documentación mínima + guía de preparación para GCP Cloud Run / Cloud SQL.

## Fuera de alcance

No incluye pedidos, stock, dashboard real, comprobantes, billing ni reportes avanzados.

## Estructura

```txt
apps/
  api/
  web/
docs/
scripts/
packages/
```

## Backend

Módulos disponibles:
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

## Frontend

Rutas:
- `/login`
- `/seller`
- `/branch-admin`
- `/tenant-admin`
- `/platform-admin`

Cada vista está protegida por `RoleGuard` consultando `GET /auth/me`.

## Cómo correr local

### Opción recomendada

```bash
docker compose up --build
```

Servicios:
- API: http://localhost:8000
- Web: http://localhost:3000

### Credenciales demo

Password para todos: `Pass1234!`
- seller@demo.com
- branch@demo.com
- tenant@demo.com
- platform@demo.com

## Migraciones y seed manuales

```bash
cd apps/api
alembic upgrade head
python scripts_seed.py
uvicorn app.main:app --reload
```

## Principios de diseño aplicados

- `tenant_id` en entidades tenant-scoped.
- Preparación de contexto `branch_id` para operación futura.
- Autorización resuelta en backend; frontend no determina permisos.
- Tenant derivado del usuario autenticado para roles tenant-scoped.
- Monolito modular para acelerar iteración manteniendo mantenibilidad.
