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
