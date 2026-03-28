from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import jwt
import pytest

from src.db.relational.entities.user import User
from src.services.auth import AuthService


@pytest.fixture
def mock_session_and_factory():
    session = AsyncMock()

    @asynccontextmanager
    async def factory():
        yield session

    return session, factory


@pytest.fixture
def auth_service(mock_session_and_factory):
    _, factory = mock_session_and_factory
    return AuthService(factory, secret="test_secret", algorithm="HS256", expire_minutes=60)


def _make_user(**overrides):
    defaults = dict(id=42, email="test@example.com", hashed_password="hashed_pwd")
    defaults.update(overrides)
    user = MagicMock(spec=User)
    for k, v in defaults.items():
        setattr(user, k, v)
    return user


@patch("src.services.auth.password_hash")
@patch("src.services.auth.UserRepository")
async def test_register_success(mock_repo_cls, mock_pw_hash, auth_service):
    mock_repo = AsyncMock()
    mock_repo.get_by_email.return_value = None
    mock_repo.add.return_value = 1
    mock_repo_cls.return_value = mock_repo
    mock_pw_hash.hash.return_value = "hashed_pwd"

    result = await auth_service.register("test@example.com", "password")

    mock_repo.get_by_email.assert_awaited_once_with("test@example.com")
    mock_repo.add.assert_awaited_once()
    assert isinstance(result, User)
    assert result.email == "test@example.com"


@patch("src.services.auth.UserRepository")
async def test_register_duplicate_email(mock_repo_cls, auth_service):
    mock_repo = AsyncMock()
    mock_repo.get_by_email.return_value = _make_user()
    mock_repo_cls.return_value = mock_repo

    with pytest.raises(ValueError, match="already exists"):
        await auth_service.register("test@example.com", "password")


@patch("src.services.auth.password_hash")
@patch("src.services.auth.UserRepository")
async def test_login_success_returns_jwt(mock_repo_cls, mock_pw_hash, auth_service):
    user = _make_user(id=42, hashed_password="hashed")
    mock_repo = AsyncMock()
    mock_repo.get_by_email.return_value = user
    mock_repo_cls.return_value = mock_repo
    mock_pw_hash.verify.return_value = True

    token = await auth_service.login("test@example.com", "password")

    assert isinstance(token, str)
    payload = jwt.decode(token, "test_secret", algorithms=["HS256"])
    assert payload["sub"] == "42"
    assert "exp" in payload


@patch("src.services.auth.UserRepository")
async def test_login_wrong_email(mock_repo_cls, auth_service):
    mock_repo = AsyncMock()
    mock_repo.get_by_email.return_value = None
    mock_repo_cls.return_value = mock_repo

    with pytest.raises(ValueError, match="Invalid email or password"):
        await auth_service.login("wrong@example.com", "password")


@patch("src.services.auth.password_hash")
@patch("src.services.auth.UserRepository")
async def test_login_wrong_password(mock_repo_cls, mock_pw_hash, auth_service):
    user = _make_user(hashed_password="hashed")
    mock_repo = AsyncMock()
    mock_repo.get_by_email.return_value = user
    mock_repo_cls.return_value = mock_repo
    mock_pw_hash.verify.return_value = False

    with pytest.raises(ValueError, match="Invalid email or password"):
        await auth_service.login("test@example.com", "wrong")


async def test_token_contains_correct_claims(auth_service):
    import time

    token = auth_service._create_token(user_id=99)

    payload = jwt.decode(token, "test_secret", algorithms=["HS256"])
    assert payload["sub"] == "99"
    assert "exp" in payload
    assert payload["exp"] > time.time()
