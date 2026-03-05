from abc import ABC, abstractmethod

from src.db.relational.db import _session_factory
from src.db.relational.repositories.recording import RecordingRepository
from src.db.cloude_storage.s3 import AsyncS3Uploader
from src.repositories.recording import AbstractRecordingRepository


class AbstractUnitOfWork(ABC):
    recordings: AbstractRecordingRepository

    @abstractmethod
    async def __aenter__(self): ...

    @abstractmethod
    async def __aexit__(self, *args): ...

    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...


class UnitOfWork(AbstractUnitOfWork):

    def __init__(self):
        self._s3: AsyncS3Uploader | None = None
        self._s3_uploaded_keys: list[str] = []

    async def __aenter__(self):
        self._session = _session_factory()
        self.recordings = RecordingRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        await self._session.close()
        if self._s3:
            await self._s3.close()

    async def commit(self):
        await self._session.commit()
        self._s3_uploaded_keys.clear()

    async def rollback(self):
        await self._session.rollback()
        if self._s3 and self._s3_uploaded_keys:
            for key in self._s3_uploaded_keys:
                try:
                    await self._s3.delete_file(key)
                except Exception:
                    pass
            self._s3_uploaded_keys.clear()


    async def _ensure_s3(self):
        if self._s3 is None:
            self._s3 = AsyncS3Uploader()
            await self._s3.connect()

    async def upload_file(self, file_obj, file_key: str) -> None:
        await self._ensure_s3()
        await self._s3.upload_file(file_obj, file_key)
        self._s3_uploaded_keys.append(file_key)

    async def get_file_url(self, file_key: str) -> str:
        await self._ensure_s3()
        return await self._s3.get_file_url(file_key)
