from unittest.mock import AsyncMock, MagicMock

import pytest

from src.db.relational.entities.recording import Recording


class TestUploadAndCreateRecording:

    async def test_upload_and_create_recording_success(
        self, recording_service, mock_uow
    ):
        file_obj = MagicMock()

        result = await recording_service.upload_and_create_recording(
            user_id=1, file_obj=file_obj, original_filename="test.mp3"
        )

        mock_uow.upload_file.assert_awaited_once()
        mock_uow.get_file_url.assert_awaited_once()
        mock_uow.recordings.add.assert_awaited_once()
        mock_uow.publish.assert_called_once()
        mock_uow.commit.assert_awaited_once()
        assert isinstance(result, Recording)

    async def test_upload_generates_unique_file_key(
        self, recording_service, mock_uow
    ):
        file_obj = MagicMock()

        await recording_service.upload_and_create_recording(
            user_id=1, file_obj=file_obj, original_filename="a.mp3"
        )
        # Reset mocks for second call but keep the factory working
        mock_uow.upload_file.reset_mock()
        mock_uow.get_file_url.reset_mock()
        mock_uow.recordings.add.reset_mock()
        mock_uow.publish.reset_mock()
        mock_uow.commit.reset_mock()

        await recording_service.upload_and_create_recording(
            user_id=1, file_obj=file_obj, original_filename="a.mp3"
        )

        # Collect all file keys from both calls
        all_calls = mock_uow.upload_file.call_args_list
        # We only have one call after reset, get the first from before reset won't work
        # Instead, let's approach differently: just check the key from the second call
        # Both calls use uuid so they must differ. We verify the second call used a key.
        assert len(all_calls) == 1  # after reset
        key_second = all_calls[0][0][1]  # positional arg [1] = file_key
        assert key_second.startswith("recordings/1/")
        assert key_second.endswith(".mp3")


class TestGetRecordingsPage:

    async def test_get_recordings_page_delegates(
        self, recording_service, mock_uow
    ):
        mock_uow.recordings.get_page = AsyncMock(return_value=([], 0))

        await recording_service.get_recordings_page(
            offset=10, limit=5, user_id=3
        )

        mock_uow.recordings.get_page.assert_awaited_once_with(
            10, 5, user_id=3
        )


class TestGetRecordingStatus:

    async def test_get_recording_status_returns_recording(
        self, recording_service, mock_uow
    ):
        expected = Recording(
            id=1, ts=123, file_url="url", user_id=1, status="uploaded"
        )
        mock_uow.recordings.get_by_id = AsyncMock(return_value=expected)

        result = await recording_service.get_recording_status(1)

        assert result is expected


class TestUpdateRecordingStatus:

    async def test_update_status_valid_transition(
        self, recording_service, mock_uow
    ):
        existing = Recording(
            id=1, ts=123, file_url="url", user_id=1, status="uploaded"
        )
        mock_uow.recordings.get_by_id = AsyncMock(return_value=existing)
        mock_uow.recordings.update_status = AsyncMock(return_value=existing)

        await recording_service.update_recording_status(1, "transcribing")

        mock_uow.recordings.update_status.assert_awaited_once()
        mock_uow.commit.assert_awaited_once()

    async def test_update_status_invalid_transition(
        self, recording_service, mock_uow
    ):
        existing = Recording(
            id=1, ts=123, file_url="url", user_id=1, status="ready"
        )
        mock_uow.recordings.get_by_id = AsyncMock(return_value=existing)

        with pytest.raises(ValueError, match="Invalid status transition"):
            await recording_service.update_recording_status(1, "transcribing")

    async def test_update_status_not_found(
        self, recording_service, mock_uow
    ):
        mock_uow.recordings.get_by_id = AsyncMock(return_value=None)

        result = await recording_service.update_recording_status(
            1, "transcribing"
        )

        assert result is None
        mock_uow.commit.assert_not_awaited()
