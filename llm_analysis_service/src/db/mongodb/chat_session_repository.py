from datetime import datetime, timezone

from llm_analysis_service.src.db.mongodb.client import MongoDBClient


class ChatSessionRepository:
    """Хранение истории чат-сессий в MongoDB. Одна сессия на запись."""

    COLLECTION_NAME = "chat_sessions"

    def __init__(self, client: MongoDBClient) -> None:
        self._collection = client.get_collection(self.COLLECTION_NAME)

    async def ensure_indexes(self) -> None:
        """Индекс по recording_id (unique — одна сессия на запись)."""
        await self._collection.create_index("recording_id", unique=True)

    async def get_history(self, recording_id: int) -> list[dict]:
        """Вернуть список сообщений для recording_id, или пустой список."""
        doc = await self._collection.find_one({"recording_id": recording_id})
        return doc["messages"] if doc else []

    async def append_messages(self, recording_id: int, messages: list[dict]) -> None:
        """Атомарный $push новых сообщений в сессию (upsert)."""
        await self._collection.update_one(
            {"recording_id": recording_id},
            {
                "$push": {"messages": {"$each": messages}},
                "$set": {"updated_at": datetime.now(timezone.utc)},
                "$setOnInsert": {"created_at": datetime.now(timezone.utc)},
            },
            upsert=True,
        )

    async def delete_session(self, recording_id: int) -> bool:
        """Удалить сессию (сброс истории). Вернуть True если удалена."""
        result = await self._collection.delete_one({"recording_id": recording_id})
        return result.deleted_count > 0
