import pytest
from unittest.mock import MagicMock
from worker.chunk.chunk_repository import ChunkRepositorySync
from shared.modules.chunk.model import Chunk


@pytest.fixture(scope="function")
def repository():
    return ChunkRepositorySync(db=MagicMock())


def test_flush_many_adds_and_flushes(repository):
    chunks = [MagicMock(spec=Chunk), MagicMock(spec=Chunk)]

    result = repository.flush_many(chunks)

    repository.db.add_all.assert_called_once_with(chunks)
    repository.db.flush.assert_called_once()
    assert result == chunks


def test_flush_many_returns_empty_list(repository):
    result = repository.flush_many([])

    repository.db.add_all.assert_called_once_with([])
    assert result == []
