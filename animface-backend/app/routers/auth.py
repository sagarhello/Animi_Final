from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest, AccessTokenResponse
from app.schemas.user import UserOut
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.dependencies import get_current_user
from app.config import settings
import uuid

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check username + email uniqueness
    result = await db.execute(
        select(User).where(or_(User.username == body.username, User.email == body.email))
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Username or email already taken")

    user = User(
        id=uuid.uuid4(),
        username=body.username,
        email=body.email,
        hashed_password=hash_password(body.password),
        avatar_emoji=body.avatar_emoji,
    )
    db.add(user)
    await db.flush()

    access = create_access_token(str(user.id))
    refresh = create_refresh_token(str(user.id))

    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(
            or_(User.username == body.username_or_email, User.email == body.username_or_email)
        )
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")

    user.last_seen = datetime.utcnow()

    access = create_access_token(str(user.id))
    refresh = create_refresh_token(str(user.id))

    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    payload = decode_token(body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")
    try:
        user_uuid = uuid.UUID(str(user_id))
    except (TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid refresh token payload")

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    access = create_access_token(str(user.id))
    return AccessTokenResponse(
        access_token=access,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=UserOut)
async def get_me(user: User = Depends(get_current_user)):
    return user
