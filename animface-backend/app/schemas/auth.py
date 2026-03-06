from pydantic import BaseModel, EmailStr, field_validator
import re


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    avatar_emoji: str = "👾"

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip().lower()
        if len(v) < 3 or len(v) > 30:
            raise ValueError("Username must be 3-30 characters")
        if not re.match(r"^[a-z0-9_\.]+$", v):
            raise ValueError("Username can only contain letters, numbers, _ and .")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    username_or_email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
