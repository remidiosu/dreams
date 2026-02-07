from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.users import User
from app.services.auth_service import AuthService


demo_router = APIRouter()

DEMO_USER_EMAIL = "demo@dreamjournal.app"


@demo_router.post("/demo")
async def demo_login(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.email == DEMO_USER_EMAIL)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demo user not found. Please run the seed script first."
        )

    access_token = AuthService().create_access_token(user.id, user.email)

    return {
        "access_token": access_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
        },
        "demo_mode": True,
    }
