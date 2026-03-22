from datetime import datetime

from src.repositories.transcription import AbstractTranscriptionRepository


class TranscriptionRepository(AbstractTranscriptionRepository):

    def __init__(self, collection):
        self._collection = collection

    async def save(self, recording_id: int, text: str, segments: list[dict]):
        result = await self._collection.insert_one({
            "recording_id": recording_id,
            "text": text,
            "segments": segments,
            "created_at": datetime.utcnow(),
        })
        return result.inserted_id
