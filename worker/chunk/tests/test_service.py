import pytest
from unittest.mock import MagicMock
from worker.chunk.chunk_service import ChunkServiceSync


@pytest.fixture(scope="function")
def service():
    return ChunkServiceSync(repo=MagicMock())


def test_create_chunks_from_text_returns_chunk_objects(service):
    chunks = ["first chunk", "second chunk"]

    # returns chunks
    service.repo.flush_many = MagicMock(side_effect=lambda chunks: chunks)

    result = service.create_chunks_from_text(chunks=chunks, document_id=1, user_id=2)

    assert len(result) == 2
    assert result[0].text == "first chunk"
    assert result[1].text == "second chunk"


