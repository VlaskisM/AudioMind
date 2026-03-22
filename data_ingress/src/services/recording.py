import uuid
from datetime import datetime
from typing import BinaryIO

from src.db.relational.entities.recording import Recording


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

    @staticmethod
    async def _create_recording(uow, file_url: str, user_id: int) -> Recording:
        recording = Recording(
            ts=int(datetime.now().timestamp()),
            file_url=file_url,
            user_id=user_id,
        )
        await uow.recordings.add(recording)
        return recording

    @staticmethod
    def _generate_file_key(user_id: int, original_filename: str) -> str:
        ext = original_filename.rsplit(".", 1)[-1] if "." in original_filename else "bin"
        unique_id = uuid.uuid4().hex[:12]
        return f"recordings/{user_id}/{unique_id}.{ext}"
