import pytest
from unittest.mock import AsyncMock, MagicMock
from api.modules.chunk.service import ChunkServiceAsync


@pytest.fixture(scope="function")
def service():
    return ChunkServiceAsync(repositoy=AsyncMock())


@pytest.mark.asyncio
async def test_get_chunks_for_doc_returns_ids(service):
    chunk = MagicMock()
    chunk.id = "abc-123"
    service.repository.get_chunks_for_doc = AsyncMock(return_value=[chunk])

    result = await service.get_chunks_for_doc(document_id=10, user_id=1)

    assert result == ["abc-123"]


@pytest.mark.asyncio
async def test_get_chunks_for_doc_empty(service):
    service.repository.get_chunks_for_doc = AsyncMock(return_value=[])

    result = await service.get_chunks_for_doc(document_id=10, user_id=1)

    assert result == []


@pytest.mark.asyncio
async def test_delete_chunks_for_doc_delegates_to_repository(service):
    await service.delete_chunks_for_doc(document_id=10, user_id=1)

    service.repository.delete_chunks_for_doc.assert_called_once_with(document_id=10, user_id=1)
