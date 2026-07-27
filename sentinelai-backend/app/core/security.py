from datetime import datetime, timezone
from typing import Any

import structlog
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

logger = structlog.get_logger(__name__)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.BCRYPT_ROUNDS,
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str | Any,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    claims = {
        "sub": str(subject),
        "iat": now,
        "exp": now + settings.JWT_ACCESS_TOKEN_EXPIRE,
        "aud": settings.JWT_AUDIENCE,
        "iss": settings.JWT_ISSUER,
        "type": "access",
    }
    if extra_claims:
        claims.update(extra_claims)

    return jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str | Any) -> str:
    now = datetime.now(timezone.utc)
    claims = {
        "sub": str(subject),
        "iat": now,
        "exp": now + settings.JWT_REFRESH_TOKEN_EXPIRE,
        "aud": settings.JWT_AUDIENCE,
        "iss": settings.JWT_ISSUER,
        "type": "refresh",
    }
    return jwt.encode(claims, settings.JWT_REFRESH_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str, is_refresh: bool = False) -> dict[str, Any]:
    secret = settings.JWT_REFRESH_SECRET_KEY if is_refresh else settings.SECRET_KEY
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
        )
        return payload
    except JWTError as e:
        logger.warning("Token decode failed", error=str(e))
        raise


def generate_api_key() -> str:
    import secrets
    return f"sk-{secrets.token_urlsafe(32)}"
