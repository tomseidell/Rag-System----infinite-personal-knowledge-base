import json
import pytest
from unittest.mock import AsyncMock, MagicMock
from api.modules.chat.service import ChatService
from shared.core.exceptions import NotFoundException


@pytest.fixture(scope="function")
def service():
    return ChatService(
        qdrant_service=AsyncMock(),
        llm_service=AsyncMock(),
        document_service=AsyncMock(),
        redis_service=AsyncMock(),
    )


async def collect(gen) -> list:
    return [item async for item in gen]


def test_create_cache_key_is_deterministic(service):
    key1 = service._create_cache_key(message="hello", user_id=1)
    key2 = service._create_cache_key(message="hello", user_id=1)
    assert key1 == key2


def test_create_cache_key_differs_by_user(service):
    assert service._create_cache_key(message="hello", user_id=1) != service._create_cache_key(message="hello", user_id=2)


def test_create_cache_key_differs_by_message(service):
    assert service._create_cache_key("hello", 1) != service._create_cache_key("world", 1)


@pytest.mark.asyncio
async def test_post_message_returns_cached_response(service):
    cached = json.dumps({"response": "cached answer", "ressources": [{"id": 1, "name": "doc.pdf"}]})

    # mock cache from redis 
    service.redis_service.get = AsyncMock(return_value=cached.encode())

    chunks = await collect(service.post_message("What is AI?", user_id=1))

    assert chunks[0] == "cached answer"
    assert json.loads(chunks[1]) == [{"id": 1, "name": "doc.pdf"}]
    service.llm_service.embed_text.assert_not_called() # skip embedding because response is in cache


@pytest.mark.asyncio
async def test_post_message_calls_llm_on_cache_miss(service):
    # mock no cache 
    service.redis_service.get = AsyncMock(return_value=None)
    # mock llm embedding
    service.llm_service.embed_text = AsyncMock(return_value=[0.1, 0.2])

    chunk = MagicMock()
    chunk.payload = {"content": "AI is great", "document_id": 5}
    service.qdrant_service.get_matching_chunks = AsyncMock(return_value=[chunk])

    service.document_service.get_document_name_and_id = AsyncMock(return_value=(5, "ai.pdf"))

    async def fake_stream(texts, user_input):
        yield "answer"

    service.llm_service.create_message = fake_stream

    # save all chunks from stream in list
    chunks = await collect(service.post_message("What is AI?", user_id=1))

    assert "answer" in chunks
    service.redis_service.set.assert_called_once() # add to cache


@pytest.mark.asyncio
async def test_post_message_skips_missing_documents(service):
    service.redis_service.get = AsyncMock(return_value=None)
    service.llm_service.embed_text = AsyncMock(return_value=[0.1])

    chunk = MagicMock()
    chunk.payload = {"content": "text", "document_id": 99}
    service.qdrant_service.get_matching_chunks = AsyncMock(return_value=[chunk])

    service.document_service.get_document_name_and_id = AsyncMock(
        side_effect=NotFoundException("document")
    )

    async def fake_stream(texts, user_input):
        yield "answer"

    service.llm_service.create_message = fake_stream

    chunks = await collect(service.post_message("What is AI?", user_id=1))

    ressources = json.loads(chunks[-1])
    assert ressources == []
