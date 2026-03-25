from src.db.mongodb.client import MongoDBClient


class DiarizationReader:
    """Читает диаризацию из коллекции diarizations."""

    COLLECTION_NAME = "diarizations"

    def __init__(self, client: MongoDBClient) -> None:
        self._collection = client.get_collection(self.COLLECTION_NAME)

    async def get_by_recording_id(self, recording_id: int) -> dict | None:
        """Возвращает документ диаризации или None."""
        return await self._collection.find_one({"recording_id": recording_id})

    async def get_speakers(self, recording_id: int) -> list[dict]:
        """Возвращает список спикеров с сегментами, или пустой список."""
        doc = await self.get_by_recording_id(recording_id)
        if doc is None:
            return []
        return doc.get("speakers", [])
