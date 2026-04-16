# Preparación mínima para GCP

## Servicios objetivo
- Cloud Run para `apps/api` y `apps/web`.
- Cloud SQL PostgreSQL para base de datos.
- Secret Manager para `DATABASE_URL` y `JWT_SECRET_KEY`.

## Pasos siguientes (fuera de Sprint 1)
- Crear pipelines CI/CD.
- Configurar VPC connector para Cloud SQL.
- Endurecer seguridad (rotación de secretos, WAF, etc.).
