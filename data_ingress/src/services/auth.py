from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from src.db.relational.db import session
from src.db.relational.entities.user import User
from src.db.relational.repositories.user import UserRepository


password_hash = PasswordHash.recommended()


class AuthService:

    def __init__(
        self,
        session_factory,
        secret: str,
        algorithm: str,
        expire_minutes: int,
    ):
        self._session_factory = session_factory
        self._secret = secret
        self._algorithm = algorithm
        self._expire_minutes = expire_minutes

    async def register(self, email: str, password: str) -> User:
        async with self._session_factory() as s:
            repo = UserRepository(s)
            existing = await repo.get_by_email(email)
            if existing is not None:
                raise ValueError("User with this email already exists")
            hashed = password_hash.hash(password)
            user = User(email=email, hashed_password=hashed)
            await repo.add(user)
            return user

    async def login(self, email: str, password: str) -> str:
        async with self._session_factory() as s:
            repo = UserRepository(s)
            user = await repo.get_by_email(email)
            if user is None:
                raise ValueError("Invalid email or password")
            if not password_hash.verify(password, user.hashed_password):
                raise ValueError("Invalid email or password")
            return self._create_token(user.id)

    def _create_token(self, user_id: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=self._expire_minutes)
        payload = {"sub": user_id, "exp": expire}
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)
