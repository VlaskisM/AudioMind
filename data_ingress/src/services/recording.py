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

    async def get_recordings_page(self, offset: int = 0, limit: int = 20, user_id: int | None = None) -> tuple[list[Recording], int]:
        async with self._uow_factory() as uow:
            return await uow.recordings.get_page(offset, limit, user_id=user_id)

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

    async def delete_recording(self, recording_id: int, user_id: int) -> bool:
        """Удалить запись: S3-файл + строку в БД."""
        async with self._uow_factory() as uow:
            recording = await uow.recordings.get_by_id(recording_id)
            if recording is None or recording.user_id != user_id:
                return False
            # Извлекаем ключ S3 из file_url (формат: recordings/{user_id}/{uuid}.{ext})
            file_key = self._extract_file_key(recording.file_url)
            if file_key:
                try:
                    await uow.delete_file(file_key)
                except Exception:
                    pass  # файл мог быть уже удалён
            await uow.recordings.delete(recording_id)
            await uow.commit()
            return True

    @staticmethod
    def _extract_file_key(file_url: str) -> str | None:
        """Извлекает S3 key из presigned URL или прямого пути."""
        # presigned URL содержит путь вида /bucket/recordings/...
        # ищем 'recordings/' в URL
        marker = "recordings/"
        idx = file_url.find(marker)
        if idx == -1:
            return None
        return file_url[idx:]

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
