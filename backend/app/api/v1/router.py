from fastapi import APIRouter

from app.api.v1.endpoints import admin_tests, auth, tests

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(tests.router, prefix="/tests", tags=["tests"])
api_router.include_router(admin_tests.router, prefix="/admin/tests", tags=["admin"])
