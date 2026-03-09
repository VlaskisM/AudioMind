from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient

from src.configs.mongodb import mongo_settings
from src.repositories.transcription import AbstractTranscriptionRepository

COLLECTION_NAME = "transcriptions"


class TranscriptionRepository(AbstractTranscriptionRepository):

    def __init__(self):
        self._client = AsyncIOMotorClient(mongo_settings.url)
        self._db = self._client[mongo_settings.MONGO_DB]
        self._collection = self._db[COLLECTION_NAME]

    async def save(self, recording_id: int, text: str, segments: list[dict]) -> None:
        await self._collection.insert_one({
            "recording_id": recording_id,
            "text": text,
            "segments": segments,
            "created_at": datetime.utcnow(),
        })

    async def close(self):
        self._client.close()
