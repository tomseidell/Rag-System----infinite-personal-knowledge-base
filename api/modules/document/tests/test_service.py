import pytest
from unittest.mock import patch, AsyncMock, ANY
from api.modules.document.service import DocumentService
from shared.core.exceptions import InputError, NotFoundException
from shared.modules.document.model import Document
from datetime import datetime
from api.modules.document.schemas import DocumentContentResponse, DocumentUploadResponse
from api.clients.qdrant.exceptions import QdrantException
from api.clients.storage.exceptions import StorageException

# create mocked service
@pytest.fixture(scope="function") # fixture creates new instance after every functin call, therefore allows us to have a fresh isntance, without configurations of previous tests (e.g. mocked methods...)
def service():
    return DocumentService(
        document_repository=AsyncMock(),
        storage=AsyncMock(),
        user_repository=AsyncMock(),
        qdrant_service=AsyncMock(),
        chunk_service=AsyncMock(),
        db=AsyncMock(),
        )

@pytest.fixture(scope="function")
def mocked_existing_document():
    return Document(
    id=12,
    user_id=1,
    title="test",
    original_filename="original-filename.pdf",
    storage_path="storage.path.gcp",
    file_size=12,
    file_type="application/pdf",
    source_type="pdf",
    source_id="mocked-id",
    content_hash="sample-hash",
    status="processed",
    error_message=None,
    chunk_count=24,
    indexed_at=datetime(2026, 1, 1),
    created_at=datetime(2026, 1, 1),
)


def test_calculate_hash(service):
    """
    Method should create sha256 hash from bytes
    """
    example_string = "Hello, this is a Test"
    bytes_string = example_string.encode("utf-8") # transform string to bytes
    result = service._calculate_hash(bytes_string)

    assert result == "f8a08e274f99740446298638ef2db4e463e15d7b1a5b164a7a4822d72da1819f"

def test_create_title_from_file(service):
    """
    Method should remove all spaces from a given string
    """
    example_file_name = "This is a filename"
    result = service._create_title_from_file(example_file_name)
    assert result == "Thisisafilename"

def test_get_file_extension(service):
    """
    Method should extract file type (str after .)
    """
    example_file_name = "file.pdf"
    result = service._get_file_extension(example_file_name)
    assert result == "pdf"


# test upload document
@pytest.mark.asyncio # create async test
async def test_upload_document_too_large_file(service):
    """
    Method should remove all spaces from a given string
    """

    mocked_file = AsyncMock()
    # when .read() is called return this
    mocked_file.read.return_value = b"x" * (10 * 1024 * 1024)  # mock 10mb size

    with pytest.raises(InputError, match="too large"): # expect InputError Exception to be thrown
        await service.upload_document(user_id=1, file= mocked_file, title="test")

@pytest.mark.asyncio 
async def test_upload_document_without_filename(service):
    """
    Method should fail because of absent document filename
    """

    mocked_file = AsyncMock()
    mocked_file.filename = None

    with pytest.raises(InputError, match="is missing"): # expect InputError Exception to be thrown
        await service.upload_document(user_id=1, file= mocked_file, title="test")

@pytest.mark.asyncio 
async def test_upload_document_with_wrong_file_type(service):
    """
    Method should fail because of invalid filename ending and therefore invalid file type
    """

    mocked_file = AsyncMock()
    mocked_file.filename = "image.png"

    with pytest.raises(InputError, match="is not pdf"): # expect InputError Exception to be thrown
        await service.upload_document(user_id=1, file= mocked_file, title="test")

@pytest.mark.asyncio 
async def test_upload_document_with_existing_hash(service, mocked_existing_document):
    """
    Method should return existing Document from db, without creating a new one 
    """

    mocked_file = AsyncMock()
    mocked_file.filename = "file.pdf"
    mocked_file.read = AsyncMock(return_value=b"example pdf content") # mock async .read()
    mocked_file.content_type = "application/pdf" 

    service.document_repository.check_for_existing_hash = AsyncMock(
        return_value = mocked_existing_document
    )  

    result = await service.upload_document(user_id=2, file=mocked_file, title="test")

    assert isinstance(result, DocumentUploadResponse) # response should be of type
    assert result.id == mocked_existing_document.id

    # check for correct hash generation
    service.document_repository.check_for_existing_hash.assert_called_once_with(
        user_id=2, content_hash="4bc997d464aadc640956a5822bc2b7563dd40f88aadb71e329d3ccad9e4f7f71"  
    )

    # ensure function returns without creating new document
    service.document_repository.create_document.assert_not_called()

@pytest.mark.asyncio
async def test_upload_document(service, mocked_existing_document):
    """
    Method should return create new Document
    """

    mocked_file = AsyncMock()
    mocked_file.filename = "file.pdf"
    mocked_file.read = AsyncMock(return_value=b"example pdf content") # mock async .read()
    mocked_file.content_type = "application/pdf" 

    # hash from document should not be in database
    service.document_repository.check_for_existing_hash = AsyncMock(
        return_value = None
    )

    service.document_repository.create_document = AsyncMock(
        return_value = mocked_existing_document
    )

    # mock celery_app.send_task response
    with patch("api.modules.document.service.celery_app.send_task") as mocked_task: 
        mocked_task.return_value.task_id = "mocked-task-id" # mocked celery response
    
        result = await service.upload_document(user_id=2, file=mocked_file, title="test")

        assert isinstance(result, DocumentUploadResponse)
        assert result.id == mocked_existing_document.id
        assert result.task_id == "mocked-task-id"

        service.document_repository.create_document.assert_called_once()

        mocked_task.assert_called_once_with("process_document",
            args=[ANY, mocked_existing_document.id, 2, ANY, "application/pdf"] # 1st = String from document bytes, 3rd = unique name
        )   


# test get document
@pytest.mark.asyncio
async def test_get_non_existing_document(service):
    """
    Method should raise Exception because given document id should not be found in db
    """

    service.document_repository.get_document = AsyncMock(return_value=None)

    with pytest.raises(NotFoundException, match="document"):
        await service.get_document(user_id = 1, document_id = 14)

@pytest.mark.asyncio
async def test_get_document(service, mocked_existing_document):
    """
    Method should successfully get document with given id
    """

    service.document_repository.get_document = AsyncMock(return_value=mocked_existing_document)
    service.storage.get_file = AsyncMock(return_value=b"mocked bytes") 

    result = await service.get_document(user_id=1, document_id=12)

    assert isinstance(result, DocumentContentResponse)
    assert result.content == b"mocked bytes"
    assert result.original_filename == mocked_existing_document.original_filename


# test delete document 
@pytest.mark.asyncio
async def test_delete_non_existing_document(service):
    """
    Method should raise error, because given document id was not found in db
    """

    service.document_repository.get_document = AsyncMock(return_value = None)

    with pytest.raises(NotFoundException, match="document"):
        await service.delete_document(user_id=1, document_id= 14)


@pytest.mark.asyncio
async def test_delete_document_qdrant_fails(service, mocked_existing_document):
    """
    Method should propagate QdrantException, because Qdrant deletion fails
    """

    mocked_extended_point_list = [1,2,3,4,5,6]
    service.document_repository.get_document = AsyncMock(return_value = mocked_existing_document)
    service.chunk_service.get_chunks_for_doc = AsyncMock(return_value = mocked_extended_point_list)
    service.chunk_service.delete_chunks_for_doc = AsyncMock(return_value = None)
    
    # simulate exception in qdrant
    service.qdrant.delete_many_chunks = AsyncMock(side_effect=QdrantException(operation="async:delete_many_chunks",detail="error in qdrant"))
    service.storage.delete_file = AsyncMock(return_value=None)

    with pytest.raises(QdrantException, match="delete_many_chunks"):
        await service.delete_document(user_id=1, document_id=19)
   
   # expect function to directly forward error without executing any other function
    service.db.commit.assert_not_called()
    service.db.rollback.assert_not_called()


@pytest.mark.asyncio
async def test_delete_document_storage_fails(service, mocked_existing_document):
    """
    Method should propagate StorageException, because GCP Storage deletion fails
    """

    mocked_extended_point_list = [1,2,3,4,5,6]
    service.document_repository.get_document = AsyncMock(return_value = mocked_existing_document)
    service.chunk_service.get_chunks_for_doc = AsyncMock(return_value = mocked_extended_point_list)
    service.chunk_service.delete_chunks_for_doc = AsyncMock(return_value = None)
    service.qdrant.delete_many_chunks = AsyncMock(return_value = None)

    # simulate raised exception in storage service
    service.storage.delete_file = AsyncMock(side_effect=StorageException("File: test"))

    with pytest.raises(StorageException, match="File: test"):
        await service.delete_document(user_id=1, document_id=19)

    # expect function to directly forward error without executing any other function
    service.db.commit.assert_not_called()
    service.db.rollback.assert_not_called()


## jetzt hier noch test und simulieren, dass fehler in db.commit() kommt + test alles läuft gut