from datetime import datetime
from typing import Any

from app.schemas.base import BaseSchema


class UserBase(BaseSchema):
    email: str
    full_name: str
    is_active: bool = True
    role: str = "analyst"


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseSchema):
    email: str | None = None
    full_name: str | None = None
    is_active: bool | None = None
    role: str | None = None
    password: str | None = None


class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    last_login: datetime | None = None
    mfa_enabled: bool = False

    model_config = {"from_attributes": True}


class LoginRequest(BaseSchema):
    email: str
    password: str
    mfa_code: str | None = None


class TokenResponse(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseSchema):
    refresh_token: str


class ForgotPasswordRequest(BaseSchema):
    email: str


class ResetPasswordRequest(BaseSchema):
    token: str
    password: str


class ChangePasswordRequest(BaseSchema):
    current_password: str
    new_password: str


class AuthResponse(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
