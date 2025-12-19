import base64
from src.modules.document.exceptions import PDFProcessingException
import logging
import pymupdf

logger = logging.getLogger(__name__)


def extract_text_from_pdf(content:bytes) ->str:
    try:
        content_bytes = base64.b64decode(content)
        doc = pymupdf.open(stream=content_bytes, filetype="pdf")
        pages = []
        for page in doc:
            page_string = page.get_text()
            pages.append(page_string)
        content_str = "\n\n".join(pages)
        content_str = content_str.replace('\x00', '')
        logger.info(f"Extracted text length: {len(content_str)}")  # ← Logger
        logger.info(f"First 200 chars: {content_str[:200]}")
        return content_str
    except Exception as e:
        logger.error(f"Invalid or corrupted PDF: {str(e)}")
        raise PDFProcessingException(detail="Invalid or corrupted PDF")