from src.db.mongodb.client import MongoDBClient


class TranscriptionReader:
    """Читает транскрипции из коллекции transcriptions."""

    COLLECTION_NAME = "transcriptions"

    def __init__(self, client: MongoDBClient) -> None:
        self._collection = client.get_collection(self.COLLECTION_NAME)

    async def get_by_recording_id(self, recording_id: int) -> dict | None:
        """Возвращает документ транскрипции или None."""
        return await self._collection.find_one({"recording_id": recording_id})
