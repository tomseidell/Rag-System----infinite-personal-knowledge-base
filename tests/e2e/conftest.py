import pytest
import pytest_asyncio
import pymupdf
from httpx import AsyncClient

BASE_URL = "http://localhost:8000"


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


@pytest_asyncio.fixture(scope="session", autouse=True)
async def cleanup(client: AsyncClient, state: dict):
    from tests.e2e.test_document_upload import TEST_EMAIL, TEST_FULLNAME, TEST_PASSWORD

    await client.post(
        "/user/register",
        json={"fullname": TEST_FULLNAME, "email": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    await client.post("/user/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    await _delete_all_documents(client)
    await client.post("/user/logout")

    yield

    doc_id = state.get("document_id")
    if doc_id:
        await client.delete(f"/document/{doc_id}")
