from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import decode_token
from app.database.session import async_session_factory
from app.models.user import User

security_scheme = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
    x_api_key: Annotated[str | None, Header()] = None,
) -> User:
    if credentials:
        try:
            payload = decode_token(credentials.credentials)
        except Exception:
            raise AuthenticationError("Invalid or expired token")
        user_id = payload.get("sub")
        token_type = payload.get("type")
        if not user_id:
            raise AuthenticationError("Invalid token payload")
        if token_type != "access":
            raise AuthenticationError("Refresh token cannot be used for this endpoint")
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise AuthenticationError("User not found")
        if not user.is_active:
            raise AuthenticationError("User account is deactivated")
        return user

    if x_api_key:
        raise AuthenticationError("API key authentication not supported yet")

    raise AuthenticationError("Authentication required")


async def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)] = None,
) -> dict | None:
    if not credentials:
        return None
    try:
        payload = decode_token(credentials.credentials)
        return {"user_id": payload.get("sub"), "token_type": payload.get("type")}
    except Exception:
        return None


async def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role != "admin":
        raise AuthorizationError("Admin privileges required")
    return current_user
