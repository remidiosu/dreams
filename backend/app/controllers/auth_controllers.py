from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.users import User
from app.data_models.auth_data import UserRegister, UserLogin, TokenResponse, UserResponse
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.dependencies.auth import get_current_user


auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    auth_service = AuthService()

    if await user_repo.email_exists(data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    password_hash = auth_service.hash_password(data.password)
    user = await user_repo.create_user(
        email=data.email,
        password_hash=password_hash,
        name=data.name
    )

    access_token = auth_service.create_access_token(user.id, user.email)

    return TokenResponse(access_token=access_token)


@auth_router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    auth_service = AuthService()

    user = await user_repo.get_by_email(data.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not auth_service.verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = auth_service.create_access_token(user.id, user.email)

    return TokenResponse(access_token=access_token)


@auth_router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        timezone=current_user.timezone,
        dreams_indexed_count=current_user.dreams_indexed_count or 0,
        created_at=current_user.created_at
    )
