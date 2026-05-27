"""Career Platform API - Main application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin
from starlette.middleware.sessions import SessionMiddleware

from app.admin.auth import AdminAuth
from app.admin.views import (
    AnswerAdmin,
    QuestionAdmin,
    SpecialtyAdmin,
    TestAdmin,
    UserAdmin,
)
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import engine

# Setup logging
setup_logging()


def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Session middleware for admin
    app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # Include admin pages
    from app.admin.pages import router as admin_pages_router
    app.include_router(admin_pages_router, prefix="/admin", tags=["admin-pages"])

    # Setup admin panel
    authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)
    admin = Admin(
        app,
        engine,
        authentication_backend=authentication_backend,
        title="Career Platform Admin",
    )

    # Register admin views
    admin.add_view(UserAdmin)
    admin.add_view(SpecialtyAdmin)
    admin.add_view(TestAdmin)
    admin.add_view(QuestionAdmin)
    admin.add_view(AnswerAdmin)

    @app.get("/")
    async def root() -> dict[str, str]:
        """Root endpoint."""
        return {"message": "Career Platform API", "docs": "/docs", "admin": "/admin"}

    @app.get("/health")
    async def health() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy"}

    return app


app = create_app()
