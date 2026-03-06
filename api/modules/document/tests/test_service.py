import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from api.modules.document.service import DocumentService
from shared.core.exceptions import InputError
from shared.modules.document.model import Document
from datetime import datetime

# create mocked service
service = DocumentService(
    document_repository=AsyncMock(),
    storage=AsyncMock(),
    user_repository=AsyncMock(),
    qdrant_service=AsyncMock(),
    chunk_service=AsyncMock(),
    db=AsyncMock(),
)


mocked_existing_document = Document(
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



def test_calculate_hash():
    example_string = "Hello, this is a Test"
    bytes_string = example_string.encode("utf-8")
    result = service._calculate_hash(bytes_string)

    assert result == "f8a08e274f99740446298638ef2db4e463e15d7b1a5b164a7a4822d72da1819f"

def test_create_title_from_file():
    example_file_name = "This is a filename"
    result = service._create_title_from_file(example_file_name)
    assert result == "Thisisafilename"

def test_get_file_extension():
    example_file_name = "file.pdf"
    result = service._get_file_extension(example_file_name)
    assert result == "pdf"


# test upload document
@pytest.mark.asyncio # create async test
async def test_upload_document_too_large_file():
    mocked_file = AsyncMock()
    # when .read() is called return this
    mocked_file.read.return_value = b"x" * (10 * 1024 * 1024)  # mock 10mb size

    with pytest.raises(InputError, match="too large"): # expect InputError Exception to be thrown
        await service.upload_document(user_id=1, file= mocked_file, title="test")

@pytest.mark.asyncio 
async def test_upload_document_without_filename():
    mocked_file = AsyncMock()
    mocked_file.filename = None

    with pytest.raises(InputError, match="is missing"): # expect InputError Exception to be thrown
        await service.upload_document(user_id=1, file= mocked_file, title="test")

@pytest.mark.asyncio 
async def test_upload_document_with_wrong_file_type():
    mocked_file = AsyncMock()
    mocked_file.filename = "image.png"

    with pytest.raises(InputError, match="is not pdf"): # expect InputError Exception to be thrown
        await service.upload_document(user_id=1, file= mocked_file, title="test")

@pytest.mark.asyncio 
async def test_upload_document_with_existing_hash():
    mocked_file = AsyncMock()
    mocked_file.filename = "file.pdf"
    mocked_file.read = AsyncMock(return_value=b"example pdf content") # mock async .read()
    mocked_file.content_type = "application/pdf" 

    service.document_repository.check_for_existing_hash = AsyncMock(
        return_value = mocked_existing_document
    )  

    result = await service.upload_document(user_id=2, file=mocked_file, title="test")
    assert result.id == mocked_existing_document.id

    # also check if hash function works correctly 
    service.document_repository.check_for_existing_hash.assert_called_once_with(
        user_id=2, content_hash="4bc997d464aadc640956a5822bc2b7563dd40f88aadb71e329d3ccad9e4f7f71"  
    )
   
@pytest.mark.asyncio
async def test_upload_document():
    mocked_file = AsyncMock()
    mocked_file.filename = "file.pdf"
    mocked_file.read = AsyncMock(return_value=b"example pdf content") # mock async .read()
    mocked_file.content_type = "application/pdf" 

    service.document_repository.check_for_existing_hash = AsyncMock(
        return_value = None
    )

    service.document_repository.create_document = AsyncMock(
        return_value = mocked_existing_document
    )

    with patch("api.modules.document.service.celery_app.send_task") as mocked_task:
        mocked_task.return_value.task_id = "mocked-task-id" ## mocked task_id, response from mocked celery worker
    
        result = await service.upload_document(user_id=2, file=mocked_file, title="test")

        assert result.id == mocked_existing_document.id
        assert result.task_id == "mocked-task-id"