from datetime import datetime

from src.db.relational.entities.recording import Recording
from src.repositories.recording import AbstractRecordingRepository


class RecordingService:

    def __init__(self, repository: AbstractRecordingRepository):
        self.repository = repository

    async def create_recording(self, badge_id: str, file_url: str, user_id: int) -> Recording:
        recording = Recording(
            badge_id=badge_id,
            ts=int(datetime.now().timestamp()),
            file_url=file_url,
            user_id=user_id,
        )
        await self.repository.add(recording)
        return recording

    async def get_all_recordings(self) -> list[Recording]:
        return await self.repository.get_all()
