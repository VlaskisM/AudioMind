from abc import ABC, abstractmethod

from src.db.relational.entities.user import User


class AbstractUserRepository(ABC):

    @abstractmethod
    async def add(self, user: User) -> int:
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        ...
