# Release y rollback (API/Web)

## Criterios de release (go/no-go)

Un release a entorno productivo debe cumplir **todos** los siguientes criterios:

1. **CI en verde** en la rama a desplegar:
   - lint,
   - type-check,
   - tests,
   - migraciones en modo dry-run.
2. **Imagen de API en modo producción** (sin `--reload`) usando `docker-compose.prod.yml` + target `prod`.
3. **Migraciones aplicables** sin errores (`alembic upgrade head`) y reversibles con `alembic downgrade -1` en staging.
4. **Smoke test funcional mínimo**:
   - `GET /health` responde `200`.
   - `GET /ready` responde `200` con DB disponible.
   - Login demo o usuario de QA validado.
5. **Aprobación de negocio/QA** para cambios funcionales visibles.

## Proceso recomendado de release

1. Taggear versión (`vX.Y.Z`) desde commit con CI exitoso.
2. Desplegar primero a staging.
3. Ejecutar smoke tests en staging.
4. Desplegar a producción.
5. Monitorear 15-30 minutos:
   - errores 5xx,
   - latencia p95,
   - logs de migración/arranque,
   - consumo de DB.

## Criterios de rollback

Hacer rollback inmediato si ocurre cualquiera de estas condiciones:

- Incremento sostenido de errores 5xx > 2% por más de 5 minutos.
- `GET /ready` falla repetidamente en producción.
- Fallo de autenticación generalizado.
- Migración con impacto no esperado en datos o performance crítica.

## Procedimiento de rollback

### 1) Rollback de aplicación

1. Re-desplegar la imagen/tag anterior estable.
2. Validar smoke test:
   - `GET /health`.
   - `GET /ready`.
   - login básico.

### 2) Rollback de base de datos (si aplica)

> Solo si la migración nueva generó problema y fue diseñada para ser reversible.

1. Ejecutar downgrade controlado (ejemplo):

```bash
cd apps/api
alembic downgrade -1
```

2. Re-desplegar versión anterior de API.
3. Validar integridad de datos y métricas de error.

## Notas operativas

- Evitar releases con migraciones destructivas sin estrategia explícita de compatibilidad.
- Preferir cambios backward-compatible en al menos una versión intermedia.
- Registrar incidente + causa raíz tras cualquier rollback.
