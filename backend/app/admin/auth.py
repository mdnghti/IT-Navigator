from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.crud import user as user_crud
from app.db.session import AsyncSessionLocal


class AdminAuth(AuthenticationBackend):
    """Authentication backend for SQLAdmin."""

    async def login(self, request: Request) -> bool:
        """Handle admin login."""
        form = await request.form()
        email = form.get("username")
        password = form.get("password")

        if not email or not password:
            return False

        async with AsyncSessionLocal() as db:
            user = await user_crud.get_by_email(db, str(email))

            if not user or not verify_password(str(password), user.hashed_password):
                return False

            if not user.is_admin:
                return False

            token = create_access_token(subject=user.id)
            request.session.update({"token": token, "user_id": user.id})

        return True

    async def logout(self, request: Request) -> bool:
        """Handle admin logout."""
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        """Check if user is authenticated."""
        token = request.session.get("token")
        user_id = request.session.get("user_id")

        if not token or not user_id:
            return False

        async with AsyncSessionLocal() as db:
            user = await user_crud.get_by_id(db, user_id)
            if not user or not user.is_admin:
                return False

        return True
