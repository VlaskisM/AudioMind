from abc import ABC, abstractmethod

from motor.motor_asyncio import AsyncIOMotorClient

from src.configs.mongodb import mongo_settings
from src.db.mongodb import TranscriptionRepository
from src.messaging.publisher import RabbitMQPublisher
from src.repositories.transcription import AbstractTranscriptionRepository

COLLECTION_NAME = "transcriptions"


class AbstractUnitOfWork(ABC):
    transcriptions: AbstractTranscriptionRepository

    @abstractmethod
    async def __aenter__(self): ...

    @abstractmethod
    async def __aexit__(self, *args): ...

    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...

    @abstractmethod
    def publish(self, recording_id: int, audio_name: str) -> None: ...

    @abstractmethod
    def track_insert(self, inserted_id) -> None: ...


class UnitOfWork(AbstractUnitOfWork):

    def __init__(self):
        self._publisher = RabbitMQPublisher()
        self._pending_messages: list[dict] = []
        self._inserted_ids: list = []
        self._client: AsyncIOMotorClient | None = None

    async def __aenter__(self):
        self._client = AsyncIOMotorClient(mongo_settings.url)
        db = self._client[mongo_settings.MONGO_DB]
        collection = db[COLLECTION_NAME]
        self.transcriptions = TranscriptionRepository(collection)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        if self._client:
            self._client.close()
        await self._publisher.close()

    async def commit(self):
        for msg in self._pending_messages:
            await self._publisher.publish(msg["recording_id"], msg["audio_name"])
        self._pending_messages.clear()
        self._inserted_ids.clear()

    async def rollback(self):
        if self._client and self._inserted_ids:
            db = self._client[mongo_settings.MONGO_DB]
            collection = db[COLLECTION_NAME]
            for inserted_id in self._inserted_ids:
                try:
                    await collection.delete_one({"_id": inserted_id})
                except Exception:
                    pass
        self._inserted_ids.clear()
        self._pending_messages.clear()

    def publish(self, recording_id: int, audio_name: str) -> None:
        self._pending_messages.append({
            "recording_id": recording_id,
            "audio_name": audio_name,
        })

    def track_insert(self, inserted_id) -> None:
        self._inserted_ids.append(inserted_id)
