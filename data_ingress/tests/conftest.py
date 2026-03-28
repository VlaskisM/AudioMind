from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.services.recording import RecordingService


@pytest.fixture
def mock_uow():
    uow = AsyncMock()

    # recordings repository
    uow.recordings = AsyncMock()

    # S3 operations
    uow.upload_file = AsyncMock()
    uow.get_file_url = AsyncMock(return_value="https://s3/file.mp3")

    # publish is SYNC
    uow.publish = MagicMock()

    # commit / rollback
    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()

    # async context manager
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)

    return uow


@pytest.fixture
def mock_uow_factory(mock_uow):
    return lambda: mock_uow


@pytest.fixture
def recording_service(mock_uow_factory):
    return RecordingService(mock_uow_factory)


@pytest.fixture
def mock_session():
    session = AsyncMock()

    @asynccontextmanager
    async def session_factory():
        yield session

    return session, session_factory
