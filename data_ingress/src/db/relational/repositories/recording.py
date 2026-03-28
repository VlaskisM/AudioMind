from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.relational.entities.recording import Recording
from src.repositories.recording import AbstractRecordingRepository


class RecordingRepository(AbstractRecordingRepository):

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def add(self, recording: Recording) -> int:
        self.session.add(recording)
        await self.session.flush()
        return recording.id

    async def create(self, ts: int, file_url: str, user_id: int) -> Recording:
        recording = Recording(
            ts=ts,
            file_url=file_url,
            user_id=user_id,
        )
        self.session.add(recording)
        return recording

    async def get_by_id(self, recording_id: int) -> Recording | None:
        return await self.session.get(Recording, recording_id)

    async def get_all(self) -> list[Recording]:
        result = await self.session.execute(select(Recording))
        return list(result.scalars().all())

    async def get_by_user_id(self, user_id: int) -> list[Recording]:
        result = await self.session.execute(
            select(Recording).where(Recording.user_id == user_id)
        )
        return list(result.scalars().all())

    async def delete(self, recording_id: int) -> bool:
        recording = await self.session.get(Recording, recording_id)
        if recording is None:
            return False
        await self.session.delete(recording)
        return True

    async def get_page(self, offset: int = 0, limit: int = 20, user_id: int | None = None) -> tuple[list[Recording], int]:
        count_query = select(func.count()).select_from(Recording)
        items_query = select(Recording).order_by(Recording.ts.desc())

        if user_id is not None:
            count_query = count_query.where(Recording.user_id == user_id)
            items_query = items_query.where(Recording.user_id == user_id)

        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()

        items_result = await self.session.execute(
            items_query.offset(offset).limit(limit)
        )
        items = list(items_result.scalars().all())
        return items, total

    async def update_status(self, recording_id: int, status: str, error_message: str | None = None) -> Recording | None:
        recording = await self.get_by_id(recording_id)
        if recording is None:
            return None
        recording.status = status
        if error_message is not None:
            recording.error_message = error_message
        await self.session.flush()
        return recording
