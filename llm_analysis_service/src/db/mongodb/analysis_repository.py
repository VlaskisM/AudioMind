from datetime import datetime, timezone

from src.db.mongodb.client import MongoDBClient


class AnalysisRepository:
    """Repository для кэширования результатов анализа в MongoDB."""

    COLLECTION_NAME = "analyses"

    def __init__(self, client: MongoDBClient) -> None:
        self._collection = client.get_collection(self.COLLECTION_NAME)

    async def ensure_indexes(self) -> None:
        """Создаёт составной уникальный индекс (recording_id, analysis_type).

        Идемпотентная операция — безопасно вызывать при каждом старте.
        """
        await self._collection.create_index(
            [("recording_id", 1), ("analysis_type", 1)],
            unique=True,
        )

    async def get_cached(
        self, recording_id: int, analysis_type: str
    ) -> dict | None:
        """Возвращает кэшированный результат анализа или None."""
        return await self._collection.find_one(
            {
                "recording_id": recording_id,
                "analysis_type": analysis_type,
            }
        )

    async def save(
        self,
        recording_id: int,
        analysis_type: str,
        result: dict,
        model: str,
    ) -> None:
        """Сохраняет результат анализа. Upsert — перезаписывает если существует."""
        await self._collection.update_one(
            {"recording_id": recording_id, "analysis_type": analysis_type},
            {
                "$set": {
                    "result": result,
                    "model": model,
                    "created_at": datetime.now(timezone.utc),
                }
            },
            upsert=True,
        )
