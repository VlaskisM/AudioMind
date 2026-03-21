from datetime import datetime

from src.repositories.diarization import AbstractDiarizationRepository

DIARIZATION_COLLECTION = "diarizations"
TRANSCRIPTION_COLLECTION = "transcriptions"


class DiarizationRepository(AbstractDiarizationRepository):

    def __init__(self, collection):
        self._collection = collection

    async def save(self, recording_id: int, speakers: list[dict], num_speakers: int):
        result = await self._collection.insert_one({
            "recording_id": recording_id,
            "speakers": speakers,
            "num_speakers": num_speakers,
            "created_at": datetime.utcnow(),
        })
        return result.inserted_id


class TranscriptionReader:

    def __init__(self, collection):
        self._collection = collection

    async def get(self, recording_id: int) -> dict | None:
        return await self._collection.find_one({"recording_id": recording_id})
