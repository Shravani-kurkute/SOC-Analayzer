from datetime import datetime, timezone
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import AuthenticationError, ConflictError, NotFoundError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.user import (
    AuthResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(body: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise ConflictError("A user with this email already exists")

    user = User(
        email=body.email,
        full_name=body.full_name,
        password_hash=hash_password(body.password),
        role=body.role if body.role in ("admin", "manager", "analyst", "viewer") else "analyst",
        is_active=True,
    )
    db.add(user)
    await db.flush()

    access_token = create_access_token(subject=user.id, extra_claims={"role": user.role})
    refresh_token = create_refresh_token(subject=user.id)

    user.refresh_token = hash_password(refresh_token)
    await db.flush()
    await db.refresh(user)

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=30 * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=AuthResponse)
async def login(body: LoginRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.password_hash):
        raise AuthenticationError("Invalid email or password")

    if not user.is_active:
        raise AuthenticationError("Account is deactivated")

    access_token = create_access_token(subject=user.id, extra_claims={"role": user.role})
    refresh_token = create_refresh_token(subject=user.id)

    user.refresh_token = hash_password(refresh_token)
    user.last_login = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(user)

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=30 * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshTokenRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        payload = decode_token(body.refresh_token, is_refresh=True)
    except Exception:
        raise AuthenticationError("Invalid or expired refresh token")

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise AuthenticationError("User not found or deactivated")

    if not user.refresh_token or not verify_password(body.refresh_token, user.refresh_token):
        raise AuthenticationError("Refresh token has been revoked")

    access_token = create_access_token(subject=user.id, extra_claims={"role": user.role})
    new_refresh_token = create_refresh_token(subject=user.id)

    user.refresh_token = hash_password(new_refresh_token)
    await db.flush()

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=30 * 60,
    )


@router.post("/logout", status_code=204)
async def logout(
    body: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        payload = decode_token(body.refresh_token, is_refresh=True)
    except Exception:
        raise AuthenticationError("Invalid refresh token")

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user:
        user.refresh_token = None
        await db.flush()


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await db.refresh(current_user)
    return UserResponse.model_validate(current_user)


@router.post("/forgot-password", status_code=202)
async def forgot_password(body: ForgotPasswordRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user:
        return {"message": "If the email exists, a reset link has been sent"}

    reset_token = create_access_token(
        subject=user.id,
        extra_claims={"type": "password_reset", "purpose": "password_reset"},
    )

    logger.info("Password reset requested", user_id=user.id)

    return {"message": "If the email exists, a reset link has been sent", "reset_token": reset_token}


@router.post("/reset-password")
async def reset_password(body: ResetPasswordRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        payload = decode_token(body.token)
    except Exception:
        raise AuthenticationError("Invalid or expired reset token")

    if payload.get("purpose") != "password_reset":
        raise AuthenticationError("Invalid reset token purpose")

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundError("User")

    user.password_hash = hash_password(body.password)
    user.refresh_token = None
    await db.flush()

    return {"message": "Password has been reset successfully"}


@router.post("/change-password")
async def change_password(
    body: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if not verify_password(body.current_password, current_user.password_hash):
        raise AuthenticationError("Current password is incorrect")

    current_user.password_hash = hash_password(body.new_password)
    current_user.refresh_token = None
    await db.flush()

    return {"message": "Password changed successfully"}
