import asyncio
import json
import pytest
from httpx import AsyncClient

TEST_EMAIL = "e2e_test@test.com"
TEST_PASSWORD = "testpassword123"
TEST_FULLNAME = "E2E Test User"
POLL_INTERVAL = 2
POLL_TIMEOUT = 120


@pytest.mark.asyncio
async def test_01_register(client: AsyncClient, state: dict):
    response = await client.post(
        "/user/register",
        json={"fullname": TEST_FULLNAME, "email": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    # accept 201 (success) and 409 (already exist)
    # print unexpectrd status to console
    assert response.status_code in (201, 409,), f"Unexpected status: {response.text}"
    state["registered"] = True


@pytest.mark.asyncio
async def test_02_login(client: AsyncClient, state: dict):
    response = await client.post(
        "/user/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    # httpx stores the cookie automatically on the client for subsequent requests
    state["logged_in"] = True


@pytest.mark.asyncio
async def test_03_upload_document(client: AsyncClient, state: dict, test_pdf_bytes: bytes):
    assert state.get("logged_in"), "Skipping: user not logged in"

    response = await client.post(
        "/document/",
        # use example pdf data from fixture
        files={"file": ("ai_overview.pdf", test_pdf_bytes, "application/pdf")},
        params={"title": "AI Overview"},
    )
    # expect successful upload, print fail reason
    assert response.status_code == 201, f"Upload failed: {response.text}"

    body = response.json()
    assert body["id"]
    assert body["title"] == "AI Overview"

    state["document_id"] = body["id"]


@pytest.mark.asyncio
async def test_04_document_processing_completed(client: AsyncClient, state: dict):
    doc_id = state.get("document_id") # document which was uploaded in step before

    # skip this test if no document was saved previously
    assert doc_id, "Skipping: no document uploaded"

    elapsed = 0
    final_status = None

    while elapsed < POLL_TIMEOUT:
        # poll document status
        response = await client.get(f"/document/{doc_id}/status")
        if response.status_code == 404:
            # Worker hasn't picked up the task yet — keep waiting
            await asyncio.sleep(POLL_INTERVAL)
            elapsed += POLL_INTERVAL
            continue
        # only accept 404 (document not picked up yet) and 200 (status retrieved)
        assert response.status_code == 200, f"Status check failed: {response.text}"
        data = response.json()
        final_status = data.get("status")
        if final_status == "completed":
            break
        if final_status == "failed":
            pytest.fail(f"Document processing failed: {data.get('message')}")
        await asyncio.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL
    else:
        pytest.fail(f"Document processing timed out after {POLL_TIMEOUT}s (last status: {final_status})")

    assert final_status == "completed"


@pytest.mark.asyncio
async def test_05_document_appears_in_list(client: AsyncClient, state: dict):
    doc_id = state.get("document_id")
    assert doc_id, "Skipping: no document uploaded"

    # get user documents   
    response = await client.get("/document/")
    assert response.status_code == 200

    ids = [doc["id"] for doc in response.json()["documents"]]

    # ensure that previously created doc is in response
    assert doc_id in ids, f"Document {doc_id} not found in list: {ids}"


@pytest.mark.asyncio
async def test_06_chat_references_document(client: AsyncClient, state: dict):
    doc_id = state.get("document_id")
    assert doc_id, "Skipping: no document uploaded"

    ressources_raw = None

    async with client.stream(
        "POST",
        "/chat/",
        json={"message": "What is artificial intelligence?"}, # trigger embedding
    ) as response:
        # 
        assert response.status_code == 200, f"Chat failed: {response.text}"
        async for line in response.aiter_lines():
            if not line.startswith("data: "):
                continue
            data = line[6:]  # strip "data: " prefix
            if data == "[DONE]":
                break
            ressources_raw = data  # last value before [DONE] is the ressources JSON

    assert ressources_raw is not None, "No ressources received from chat stream"
    ressources = json.loads(ressources_raw)
    document_ids = [r["id"] for r in ressources]
    assert doc_id in document_ids, (
        f"Expected document {doc_id} in chat ressources, got: {ressources}"
    )
