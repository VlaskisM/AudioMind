from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.relational.entities.recording import Recording


class AbstractRecordingRepository(ABC):

    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    async def create(self, badge_id: str, ts: int, file_url: str, user_id: int) -> Recording:
        ...

    @abstractmethod
    async def get_by_id(self, recording_id: int) -> Recording | None:
        ...

    @abstractmethod
    async def get_all(self) -> list[Recording]:
        ...

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> list[Recording]:
        ...

    @abstractmethod
    async def get_by_badge_id(self, badge_id: str) -> list[Recording]:
        ...

    @abstractmethod
    async def delete(self, recording_id: int) -> bool:
        ...
