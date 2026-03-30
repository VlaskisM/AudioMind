from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.relational.entities.user import User
from src.repositories.user import AbstractUserRepository


class UserRepository(AbstractUserRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, user: User) -> int:
        self.session.add(user)
        await self.session.flush()
        return user.id

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
