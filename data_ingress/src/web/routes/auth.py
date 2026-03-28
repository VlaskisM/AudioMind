from fastapi import APIRouter, HTTPException, status

from src.configs.auth import auth_settings
from src.db.relational.db import session
from src.services.auth import AuthService
from src.web.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])

auth_service = AuthService(
    session_factory=session,
    secret=auth_settings.JWT_SECRET,
    algorithm=auth_settings.JWT_ALGORITHM,
    expire_minutes=auth_settings.JWT_EXPIRE_MINUTES,
)


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register(body: RegisterRequest):
    try:
        user = await auth_service.register(email=body.email, password=body.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return user


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    try:
        token = await auth_service.login(email=body.email, password=body.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return TokenResponse(access_token=token)
