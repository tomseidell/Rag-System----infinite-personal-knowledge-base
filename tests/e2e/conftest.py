import pytest
import pytest_asyncio
import pymupdf
from httpx import AsyncClient

BASE_URL = "http://localhost:8000"
QDRANT_URL = "http://localhost:6333"
QDRANT_COLLECTION = "second_brain"


@pytest.fixture(scope="session")
def test_pdf_bytes() -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text(
        (72, 72),
        "Artificial intelligence (AI) is the simulation of human intelligence by machines. "
        "Machine learning is a subset of AI that enables systems to learn from data automatically. "
        "Deep learning uses neural networks with many layers to recognise patterns and solve complex problems.",
    )
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


@pytest_asyncio.fixture(scope="session")
async def client():
    async with AsyncClient(base_url=BASE_URL, follow_redirects=True) as c:
        yield c


@pytest.fixture(scope="session")
def state() -> dict:
    """Shared mutable state passed between sequential e2e tests."""
    return {}


async def _delete_all_documents(client: AsyncClient) -> None:
    """Paginate through all documents and delete each one (DB + Qdrant + Storage)."""
    cursor = None
    while True:
        params = {"cursor": cursor} if cursor else {}
        response = await client.get("/document/", params=params)
        if response.status_code != 200:
            break
        body = response.json()
        for doc in body.get("documents", []):
            await client.delete(f"/document/{doc['id']}")
        cursor = body.get("next_cursor")
        if not cursor:
            break


async def _delete_orphaned_qdrant_vectors(user_id: int) -> None:
    """Delete all Qdrant vectors for this user — catches orphaned vectors not in DB."""
    async with AsyncClient(base_url=QDRANT_URL) as qdrant:
        await qdrant.post(
            f"/collections/{QDRANT_COLLECTION}/points/delete",
            json={"filter": {"must": [{"key": "user_id", "match": {"value": user_id}}]}},
        )


@pytest_asyncio.fixture(scope="session", autouse=True)
async def cleanup(client: AsyncClient, state: dict):
    from tests.e2e.test_document_upload import TEST_EMAIL, TEST_FULLNAME, TEST_PASSWORD

    # Register (idempotent) and login to get user_id
    register_resp = await client.post(
        "/user/register",
        json={"fullname": TEST_FULLNAME, "email": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    await client.post("/user/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})

    # Delete all DB documents (also cleans Qdrant + Storage via the API)
    await _delete_all_documents(client)

    # Delete any orphaned Qdrant vectors (documents deleted from DB but not Qdrant)
    user_id = register_resp.json().get("id") if register_resp.status_code == 201 else None
    if user_id:
        await _delete_orphaned_qdrant_vectors(user_id)

    await client.post("/user/logout")

    yield

    # Teardown: delete the document created in this session
    doc_id = state.get("document_id")
    if doc_id:
        await client.delete(f"/document/{doc_id}")
