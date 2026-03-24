import uuid
from datetime import datetime
from typing import BinaryIO

from src.db.relational.entities.recording import Recording


ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "uploaded": {"transcribing"},
    "transcribing": {"diarizing", "failed"},
    "diarizing": {"ready", "failed"},
    "failed": set(),
    "ready": set(),
}


class RecordingService:

    def __init__(self, uow_factory):
        self._uow_factory = uow_factory

    async def upload_and_create_recording(
        self,
        user_id: int,
        file_obj: BinaryIO,
        original_filename: str,
    ) -> Recording:
        async with self._uow_factory() as uow:
            file_key = self._generate_file_key(user_id, original_filename)
            await uow.upload_file(file_obj, file_key)
            file_url = await uow.get_file_url(file_key)
            recording = await self._create_recording(
                uow,
                file_url=file_url,
                user_id=user_id,
                original_filename=original_filename,
            )
            uow.publish(recording.id, file_key)
            await uow.commit()
            return recording

    async def create_recording(self, file_url: str, user_id: int) -> Recording:
        async with self._uow_factory() as uow:
            recording = await self._create_recording(
                uow,
                file_url=file_url,
                user_id=user_id,
            )
            await uow.commit()
            return recording

    async def get_all_recordings(self) -> list[Recording]:
        async with self._uow_factory() as uow:
            return await uow.recordings.get_all()

    async def get_recording_status(self, recording_id: int) -> Recording | None:
        async with self._uow_factory() as uow:
            return await uow.recordings.get_by_id(recording_id)

    async def get_recordings_page(self, offset: int = 0, limit: int = 20) -> tuple[list[Recording], int]:
        async with self._uow_factory() as uow:
            return await uow.recordings.get_page(offset, limit)

    async def update_recording_status(
        self, recording_id: int, status: str, error_message: str | None = None
    ) -> Recording | None:
        async with self._uow_factory() as uow:
            existing = await uow.recordings.get_by_id(recording_id)
            if existing is None:
                return None
            allowed = ALLOWED_TRANSITIONS.get(existing.status, set())
            if status not in allowed:
                raise ValueError(
                    f"Invalid status transition: '{existing.status}' -> '{status}'. "
                    f"Allowed: {allowed or 'none (terminal state)'}"
                )
            recording = await uow.recordings.update_status(recording_id, status, error_message)
            await uow.commit()
            return recording

    @staticmethod
    async def _create_recording(
        uow, file_url: str, user_id: int, original_filename: str | None = None
    ) -> Recording:
        recording = Recording(
            ts=int(datetime.now().timestamp()),
            file_url=file_url,
            user_id=user_id,
            original_filename=original_filename,
        )
        await uow.recordings.add(recording)
        return recording

    @staticmethod
    def _generate_file_key(user_id: int, original_filename: str) -> str:
        ext = original_filename.rsplit(".", 1)[-1] if "." in original_filename else "bin"
        unique_id = uuid.uuid4().hex[:12]
        return f"recordings/{user_id}/{unique_id}.{ext}"
