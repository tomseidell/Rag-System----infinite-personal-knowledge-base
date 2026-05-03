import pytest
from unittest.mock import AsyncMock, MagicMock
from api.modules.document.repository import DocumentRepository
from shared.core.exceptions import DatabaseException
from api.modules.document.schemas import DocumentCreate
from sqlalchemy.exc import SQLAlchemyError




@pytest.fixture(scope="function") # fixture creates new instance after every functin call, therefore allows us to have a fresh isntance, without configurations of previous tests (e.g. mocked methods...)
def repository():
    return DocumentRepository(
        db=AsyncMock(),
        )

@pytest.fixture(scope="function")
def mocked_document_input():
    return DocumentCreate(
    user_id = 12,
    title = "Test",
    original_filename =  "test",
    source_type =  "pdf",
    content_hash = "sample-hash",
    file_size = 12,
    file_type = "application/pdf"
)



@pytest.mark.asyncio
async def test_create_document_database_exception(repository, mocked_document_input):
    """
    Method should fail because of a Database Exception
    """

    repository.db.add = MagicMock(side_effect= SQLAlchemyError("DB error")) 

    with pytest.raises(DatabaseException, match="create_document"): # expect InputError Exception to be thrown
        await repository.create_document(data=mocked_document_input)

    repository.db.rollback.assert_called_once() 
    repository.db.commit.assert_not_called()
    repository.db.refresh.assert_not_called()


@pytest.mark.asyncio
async def test_create_document(repository, mocked_document_input):
    """
    Method should successfully create new document in db
    """

    repository.db.add = MagicMock() 

    await repository.create_document(data=mocked_document_input)


    repository.db.rollback.assert_not_called()
    repository.db.commit.assert_called_once()
    repository.db.refresh.assert_called_once()