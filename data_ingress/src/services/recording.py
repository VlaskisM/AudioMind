from src.db.relational.db import async_session
from src.db.relational.repositories.recording import RecordingRepository
from src.web.schemas.recording import RecordingCreate, RecordingResponse


class RecordingService:

    @staticmethod
    def _to_response(recording) -> RecordingResponse:
        return RecordingResponse.model_validate(recording)

    @staticmethod
    def _to_response_list(recordings) -> list[RecordingResponse]:
        return [RecordingResponse.model_validate(r) for r in recordings]

    async def create(self, data: RecordingCreate) -> RecordingResponse:
        async with async_session() as session:
            repo = RecordingRepository(session)
            recording = await repo.create(
                badge_id=data.badge_id,
                ts=data.ts,
                file_url=data.file_url,
                user_id=data.user_id,
            )
            return self._to_response(recording)

    async def get_all(self) -> list[RecordingResponse]:
        async with async_session() as session:
            repo = RecordingRepository(session)
            recordings = await repo.get_all()
            return self._to_response_list(recordings)

    async def get_by_id(self, recording_id: int) -> RecordingResponse | None:
        async with async_session() as session:
            repo = RecordingRepository(session)
            recording = await repo.get_by_id(recording_id)
            if recording is None:
                return None
            return self._to_response(recording)

    async def get_by_user_id(self, user_id: int) -> list[RecordingResponse]:
        async with async_session() as session:
            repo = RecordingRepository(session)
            recordings = await repo.get_by_user_id(user_id)
            return self._to_response_list(recordings)

    async def get_by_badge_id(self, badge_id: str) -> list[RecordingResponse]:
        async with async_session() as session:
            repo = RecordingRepository(session)
            recordings = await repo.get_by_badge_id(badge_id)
            return self._to_response_list(recordings)

    async def delete(self, recording_id: int) -> bool:
        async with async_session() as session:
            repo = RecordingRepository(session)
            return await repo.delete(recording_id)
