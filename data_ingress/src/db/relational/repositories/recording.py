from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.relational.entities.recording import Recording


class RecordingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, badge_id: str, ts: int, file_url: str, user_id: int) -> Recording:
        recording = Recording(
            badge_id=badge_id,
            ts=ts,
            file_url=file_url,
            user_id=user_id,
        )
        self.session.add(recording)
        await self.session.commit()
        await self.session.refresh(recording)
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

    async def get_by_badge_id(self, badge_id: str) -> list[Recording]:
        result = await self.session.execute(
            select(Recording).where(Recording.badge_id == badge_id)
        )
        return list(result.scalars().all())

    async def delete(self, recording_id: int) -> bool:
        recording = await self.get_by_id(recording_id)
        if recording is None:
            return False
        await self.session.delete(recording)
        await self.session.commit()
        return True
