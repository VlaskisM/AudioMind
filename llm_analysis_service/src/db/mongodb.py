from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection


class MongoDBClient:
    """Управляет подключением к MongoDB через Motor."""

    def __init__(self, url: str, database: str) -> None:
        self._client: AsyncIOMotorClient = AsyncIOMotorClient(url)
        self._db: AsyncIOMotorDatabase = self._client[database]

    def get_collection(self, name: str) -> AsyncIOMotorCollection:
        """Возвращает коллекцию по имени."""
        return self._db[name]

    async def close(self) -> None:
        """Закрывает соединение с MongoDB."""
        self._client.close()


class TranscriptionReader:
    """Читает транскрипции из коллекции transcriptions."""

    COLLECTION_NAME = "transcriptions"

    def __init__(self, client: MongoDBClient) -> None:
        self._collection = client.get_collection(self.COLLECTION_NAME)

    async def get_by_recording_id(self, recording_id: int) -> dict | None:
        """Возвращает документ транскрипции или None."""
        return await self._collection.find_one({"recording_id": recording_id})


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
