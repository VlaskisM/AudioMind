from unittest.mock import AsyncMock, MagicMock

import pytest

from src.db.relational.entities.recording import Recording
from src.db.relational.repositories.recording import RecordingRepository


@pytest.fixture
def mock_session():
    session = AsyncMock()
    # session.add is synchronous in SQLAlchemy
    session.add = MagicMock()
    return session


@pytest.fixture
def repo(mock_session):
    return RecordingRepository(mock_session)


def _make_recording(**overrides):
    defaults = dict(id=1, ts=100, file_url="https://s3/file.mp3", user_id=1, status="uploaded",
                    original_filename=None, error_message=None)
    defaults.update(overrides)
    rec = MagicMock(spec=Recording)
    for k, v in defaults.items():
        setattr(rec, k, v)
    return rec


async def test_add_calls_session_add_and_flush(repo, mock_session):
    recording = _make_recording()
    await repo.add(recording)

    mock_session.add.assert_called_once_with(recording)
    mock_session.flush.assert_awaited_once()


async def test_get_by_id_delegates_to_session_get(repo, mock_session):
    recording = _make_recording()
    mock_session.get.return_value = recording

    result = await repo.get_by_id(1)

    mock_session.get.assert_awaited_once_with(Recording, 1)
    assert result is recording


async def test_get_by_id_returns_none(repo, mock_session):
    mock_session.get.return_value = None

    result = await repo.get_by_id(1)

    assert result is None


async def test_update_status_changes_status_and_flushes(repo, mock_session):
    recording = _make_recording(status="uploaded")
    mock_session.get.return_value = recording

    result = await repo.update_status(1, "transcribing")

    assert recording.status == "transcribing"
    mock_session.flush.assert_awaited()
    assert result is recording


async def test_update_status_sets_error_message(repo, mock_session):
    recording = _make_recording(status="uploaded")
    mock_session.get.return_value = recording

    result = await repo.update_status(1, "failed", error_message="timeout")

    assert recording.status == "failed"
    assert recording.error_message == "timeout"
    assert result is recording


async def test_get_page_returns_items_and_count(repo, mock_session):
    rec1 = _make_recording(id=1)
    rec2 = _make_recording(id=2)

    count_result = MagicMock()
    count_result.scalar_one.return_value = 42

    items_result = MagicMock()
    items_result.scalars.return_value.all.return_value = [rec1, rec2]

    mock_session.execute = AsyncMock(side_effect=[count_result, items_result])

    items, total = await repo.get_page(offset=0, limit=20, user_id=1)

    assert total == 42
    assert items == [rec1, rec2]
    assert mock_session.execute.await_count == 2
