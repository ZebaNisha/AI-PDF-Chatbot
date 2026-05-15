from typing import Any

from fastapi import HTTPException, status

from app.core.security import create_access_token, create_refresh_token, verify_password
from app.db.models.user import User
from app.repositories.user import UserRepository
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserLogin


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_user(self, user_in: UserCreate) -> User:
        user = await self.user_repo.get_by_email(email=user_in.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user with this email already exists in the system.",
            )
        user = await self.user_repo.create(user_in)
        return user

    async def authenticate(self, user_in: UserLogin) -> User | None:
        user = await self.user_repo.get_by_email(email=user_in.email)
        if not user:
            return None
        if not verify_password(user_in.password, user.hashed_password):
            return None
        return user

    def create_token_pair(self, subject: str | Any) -> Token:
        return Token(
            access_token=create_access_token(subject=subject),
            refresh_token=create_refresh_token(subject=subject),
            token_type="bearer",
        )
