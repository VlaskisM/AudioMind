from typing import Type

from src.db.relational import db
from src.db.relational.entities.recording import Recording
from src.repositories.recording import AbstractRecordingRepository
from src.web.schemas.recording import RecordingCreate


class RecordingService:

    def __init__(self, repository_class: Type[AbstractRecordingRepository]):
        self.repository_class = repository_class

    async def create(self, data: RecordingCreate) -> Recording:
        async with db.session() as session:
            repo = self.repository_class(session)
            recording = await repo.create(
                badge_id=data.badge_id,
                ts=data.ts,
                file_url=data.file_url,
                user_id=data.user_id,
            )
        return recording

    async def get_all(self) -> list[Recording]:
        async with db.session() as session:
            repo = self.repository_class(session)
            return await repo.get_all()

    async def get_by_id(self, recording_id: int) -> Recording | None:
        async with db.session() as session:
            repo = self.repository_class(session)
            return await repo.get_by_id(recording_id)

    async def get_by_user_id(self, user_id: int) -> list[Recording]:
        async with db.session() as session:
            repo = self.repository_class(session)
            return await repo.get_by_user_id(user_id)

    async def get_by_badge_id(self, badge_id: str) -> list[Recording]:
        async with db.session() as session:
            repo = self.repository_class(session)
            return await repo.get_by_badge_id(badge_id)

    async def delete(self, recording_id: int) -> bool:
        async with db.session() as session:
            repo = self.repository_class(session)
            return await repo.delete(recording_id)
