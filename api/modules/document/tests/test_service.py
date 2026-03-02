import pytest
from unittest.mock import AsyncMock
from api.modules.document.service import DocumentService
from shared.core.exceptions import InputError, NotFoundException

# create mocked service
service = DocumentService(
    document_repository=AsyncMock(),
    storage=AsyncMock(),
    user_repository=AsyncMock(),
    qdrant_service=AsyncMock(),
    chunk_service=AsyncMock(),
    db=AsyncMock(),
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


@pytest.mark.asyncio # create async test
async def test_upload_document():
    mocked_file = AsyncMock()
    # when .read() is called return this
    mocked_file.read.return_value = b"x" * (10 * 1024 * 1024)  # mock 10mb size

    with pytest.raises(InputError): # expect InputError Exception to be thrown
        await service.upload_document(user_id=1, file= mocked_file, title="test")


