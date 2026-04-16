from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.roles import router as roles_router
from app.api.routes.tenants import router as tenants_router
from app.api.routes.branches import router as branches_router
from app.api.routes.users import router as users_router
from app.api.exception_handlers import register_exception_handlers
from app.core.config import settings

app = FastAPI(title=settings.app_name)
register_exception_handlers(app)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(roles_router)
app.include_router(tenants_router)
app.include_router(branches_router)
app.include_router(users_router)
