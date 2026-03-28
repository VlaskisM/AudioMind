from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.db.uow import UnitOfWork


@patch("src.db.uow.RabbitMQPublisher")
@patch("src.db.uow._session_factory")
class TestUnitOfWorkCommit:

    async def test_commit_publishes_pending_messages(
        self, mock_session_factory, mock_publisher_cls
    ):
        mock_session = AsyncMock()
        mock_session_factory.return_value = mock_session

        mock_publisher = AsyncMock()
        mock_publisher_cls.return_value = mock_publisher

        uow = UnitOfWork()
        async with uow:
            uow.publish(1, "f1.mp3")
            uow.publish(2, "f2.mp3")
            await uow.commit()

        assert mock_publisher.publish.await_count == 2
        assert uow._pending_messages == []

    async def test_commit_clears_s3_keys(
        self, mock_session_factory, mock_publisher_cls
    ):
        mock_session = AsyncMock()
        mock_session_factory.return_value = mock_session

        mock_publisher = AsyncMock()
        mock_publisher_cls.return_value = mock_publisher

        uow = UnitOfWork()
        async with uow:
            uow._s3_uploaded_keys = ["key1"]
            await uow.commit()

        assert uow._s3_uploaded_keys == []


@patch("src.db.uow.RabbitMQPublisher")
@patch("src.db.uow._session_factory")
class TestUnitOfWorkRollback:

    async def test_rollback_deletes_s3_keys(
        self, mock_session_factory, mock_publisher_cls
    ):
        mock_session = AsyncMock()
        mock_session_factory.return_value = mock_session

        mock_publisher = AsyncMock()
        mock_publisher_cls.return_value = mock_publisher

        mock_s3 = AsyncMock()

        uow = UnitOfWork()
        async with uow:
            uow._s3 = mock_s3
            uow._s3_uploaded_keys = ["key1", "key2"]
            await uow.rollback()

        assert mock_s3.delete_file.await_count == 2
        assert uow._s3_uploaded_keys == []

    async def test_rollback_clears_pending_messages(
        self, mock_session_factory, mock_publisher_cls
    ):
        mock_session = AsyncMock()
        mock_session_factory.return_value = mock_session

        mock_publisher = AsyncMock()
        mock_publisher_cls.return_value = mock_publisher

        uow = UnitOfWork()
        async with uow:
            uow.publish(1, "f.mp3")
            await uow.rollback()

        assert uow._pending_messages == []


@patch("src.db.uow.RabbitMQPublisher")
@patch("src.db.uow._session_factory")
class TestUnitOfWorkAexit:

    async def test_aexit_calls_rollback_on_exception(
        self, mock_session_factory, mock_publisher_cls
    ):
        mock_session = AsyncMock()
        mock_session_factory.return_value = mock_session

        mock_publisher = AsyncMock()
        mock_publisher_cls.return_value = mock_publisher

        uow = UnitOfWork()
        with pytest.raises(RuntimeError):
            async with uow:
                raise RuntimeError("test error")

        mock_session.rollback.assert_awaited()
