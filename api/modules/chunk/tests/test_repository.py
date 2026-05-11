import pytest
from unittest.mock import AsyncMock
from sqlalchemy.exc import SQLAlchemyError
from api.modules.chunk.repository import ChunkRepository
from shared.core.exceptions import DatabaseException


@pytest.fixture(scope="function")
def repository():
    return ChunkRepository(db=AsyncMock())



@pytest.mark.asyncio
async def test_get_chunks_for_doc_database_exception(repository):
    repository.db.execute = AsyncMock(side_effect=SQLAlchemyError("DB error"))

    with pytest.raises(DatabaseException, match="get chunks for document"):
        await repository.get_chunks_for_doc(user_id=1, document_id=10)



@pytest.mark.asyncio
async def test_delete_chunks_for_doc_database_exception(repository):
    repository.db.execute = AsyncMock(side_effect=SQLAlchemyError("DB error"))

    with pytest.raises(DatabaseException, match="delete chunks for document"):
        await repository.delete_chunks_for_doc(user_id=1, document_id=10)
