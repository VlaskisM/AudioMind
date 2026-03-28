from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.relational.entities.recording import Recording


class AbstractRecordingRepository(ABC):

    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    async def add(self, recording: Recording) -> int:
        ...

    @abstractmethod
    async def create(self, ts: int, file_url: str, user_id: int) -> Recording:
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
    async def delete(self, recording_id: int) -> bool:
        ...

    @abstractmethod
    async def get_page(self, offset: int = 0, limit: int = 20, user_id: int | None = None) -> tuple[list[Recording], int]:
        ...

    @abstractmethod
    async def update_status(self, recording_id: int, status: str, error_message: str | None = None) -> Recording | None:
        ...
