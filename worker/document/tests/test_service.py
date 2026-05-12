import base64
import pytest
import pymupdf
from unittest.mock import MagicMock
from worker.document.document_service import DocumentService
from worker.document.exceptions import PDFProcessingException


@pytest.fixture(scope="module")
def service():
    return DocumentService(repository=MagicMock())


@pytest.fixture(scope="module")
def valid_pdf_base64() -> str:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello world. This is a test PDF.")
    pdf_bytes = doc.tobytes()
    doc.close()
    return base64.b64encode(pdf_bytes).decode("utf-8")



def test_extract_text_returns_string(service, valid_pdf_base64):
    result = service.extract_text_from_pdf(valid_pdf_base64)

    assert isinstance(result, str)
    assert "Hello world" in result


def test_extract_text_raises_on_invalid_base64(service):
    with pytest.raises(PDFProcessingException):
        service.extract_text_from_pdf("string input")


def test_extract_text_raises_on_invalid_pdf(service):
    invalid_pdf = base64.b64encode(b"not a pdf").decode("utf-8")

    with pytest.raises(PDFProcessingException):
        service.extract_text_from_pdf(invalid_pdf)


def test_split_text_returns_chunks(service):
    text = "This is a sentence. " * 200

    chunks = service.split_text(text)

    assert isinstance(chunks, list)
    assert len(chunks) > 0
    assert all(isinstance(c, str) for c in chunks)


