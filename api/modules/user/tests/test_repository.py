import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.exc import SQLAlchemyError
from api.modules.user.repository import UserRepository
from shared.core.exceptions import DatabaseException


@pytest.fixture(scope="function")
def repository():
    return UserRepository(db=AsyncMock())


@pytest.mark.asyncio
async def test_create_user_database_exception(repository):

    # mock db exception
    repository.db.add = MagicMock(side_effect=SQLAlchemyError("DB error"))

    with pytest.raises(DatabaseException, match="create_user"):
        await repository.create_user(full_name="Tom", email="tom@test.com", hashed_password="hash")

    repository.db.rollback.assert_called_once()
    repository.db.commit.assert_not_called()


@pytest.mark.asyncio
async def test_create_user(repository):
    repository.db.add = MagicMock()
    await repository.create_user(full_name="Tom", email="tom@test.com", hashed_password="hash")

    repository.db.commit.assert_called_once()
    repository.db.refresh.assert_called_once()
    repository.db.rollback.assert_not_called()


@pytest.mark.asyncio
async def test_get_user_by_mail_database_exception(repository):

    # mock database exception
    repository.db.execute = AsyncMock(side_effect=SQLAlchemyError("DB error"))

    with pytest.raises(DatabaseException, match="get_user_by_mail"):
        await repository.get_user_by_mail("tom@test.com")


@pytest.mark.asyncio
async def test_get_user_by_id_database_exception(repository):

    # mock database exception
    repository.db.execute = AsyncMock(side_effect=SQLAlchemyError("DB error"))

    with pytest.raises(DatabaseException, match="get_user_by_id"):
        await repository.get_user_by_id(1)


@pytest.mark.asyncio
async def test_update_last_login_database_exception(repository):

    # mock database exception
    repository.db.execute = AsyncMock(side_effect=SQLAlchemyError("DB error"))

    with pytest.raises(DatabaseException, match="update_last_login"):
        await repository.update_last_login(1)

    repository.db.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_update_refresh_token_database_exception(repository):

    # mock database exception
    repository.db.execute = AsyncMock(side_effect=SQLAlchemyError("DB error"))

    with pytest.raises(DatabaseException, match="update_refresh_token"):
        await repository.update_refresh_token(1, "token")

    repository.db.rollback.assert_called_once()
