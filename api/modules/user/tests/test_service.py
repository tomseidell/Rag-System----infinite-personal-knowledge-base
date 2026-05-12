import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from api.modules.user.service import UserService
from api.modules.user.schemas import UserRegistration, UserLogin
from api.modules.user.exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
    InvalidCredentialsException,
    InvalidTokenException,
)


@pytest.fixture(scope="function")
def service():
    return UserService(user_repository=AsyncMock())


@pytest.fixture
def registration():
    return UserRegistration(fullname="Tom", email="tom@test.com", password="secret123")


@pytest.fixture
def login():
    return UserLogin(email="tom@test.com", password="secret123")



@pytest.mark.asyncio
async def test_create_user_raises_if_already_exists(service, registration):
    service.user_repository.get_user_by_mail = AsyncMock(return_value=MagicMock())

    with pytest.raises(UserAlreadyExistsException):
        await service.create_user(registration)

    service.user_repository.create_user.assert_not_called()



@pytest.mark.asyncio
async def test_login_user_raises_if_user_not_found(service, login):
    service.user_repository.get_user_by_mail = AsyncMock(return_value=None)

    with pytest.raises(UserNotFoundException):
        await service.login_user(login)
    
    service.user_repository.update_last_login.assert_not_called()



@pytest.mark.asyncio
async def test_login_user_raises_on_wrong_password(service, login):
    db_user = MagicMock(hashed_password="wronghash")
    service.user_repository.get_user_by_mail = AsyncMock(return_value=db_user)

    # mock verify password util
    with patch("api.modules.user.service.verify_password", return_value=False):
        with pytest.raises(InvalidCredentialsException):
            await service.login_user(login)

    service.user_repository.update_last_login.assert_not_called()



@pytest.mark.asyncio
async def test_login_user_returns_tokens(service, login):
    db_user = MagicMock(id=1, hashed_password="hash")
    service.user_repository.get_user_by_mail = AsyncMock(return_value=db_user)

    with patch("api.modules.user.service.verify_password", return_value=True):
        result = await service.login_user(login)

    assert result.access_token
    assert result.refresh_token
    service.user_repository.update_last_login.assert_called_once_with(1)
    service.user_repository.update_refresh_token.assert_called_once()



@pytest.mark.asyncio
async def test_handle_refresh_raises_if_user_not_found(service):
    with patch("api.modules.user.service.decode_refresh_token", return_value=1):
        service.user_repository.get_user_by_id = AsyncMock(return_value=None)

        with pytest.raises(UserNotFoundException):
            await service.handle_refresh("some-token")


@pytest.mark.asyncio
async def test_handle_refresh_raises_if_no_token_stored(service):
    db_user = MagicMock(refresh_token=None)
    with patch("api.modules.user.service.decode_refresh_token", return_value=1):
        service.user_repository.get_user_by_id = AsyncMock(return_value=db_user)

        with pytest.raises(InvalidTokenException):
            await service.handle_refresh("some-token")


@pytest.mark.asyncio
async def test_handle_refresh_raises_on_invalid_token(service):
    db_user = MagicMock(refresh_token="stored-hash")
    with patch("api.modules.user.service.decode_refresh_token", return_value=1):
        service.user_repository.get_user_by_id = AsyncMock(return_value=db_user)
        with patch("api.modules.user.service.verify_refresh_token", return_value=False):
            with pytest.raises(InvalidTokenException):
                await service.handle_refresh("some-token")


@pytest.mark.asyncio
async def test_handle_refresh_returns_new_tokens(service):
    db_user = MagicMock(refresh_token="stored-hash")
    with patch("api.modules.user.service.decode_refresh_token", return_value=1):
        service.user_repository.get_user_by_id = AsyncMock(return_value=db_user)
        with patch("api.modules.user.service.verify_refresh_token", return_value=True):
            result = await service.handle_refresh("some-token")

    assert result.access_token
    assert result.refresh_token
    service.user_repository.update_refresh_token.assert_called_once()
