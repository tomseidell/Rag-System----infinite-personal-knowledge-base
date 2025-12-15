from PyPDF2 import PdfReader
from io import BytesIO
import base64
from src.modules.document.exceptions import PDFProcessingException
import logging

logger = logging.getLogger(__name__)


def extract_text_from_pdf(content:bytes) ->str:
    try:
        content_bytes = base64.b64decode(content)
        reader = PdfReader(BytesIO(content_bytes)) # create new file with BytesIO wrapper => keeps file properties like read
        pages = []
        for page in reader.pages:
            page_string = page.extract_text()
            pages.append(page_string)
        return "\n".join(pages)
    except Exception as e:
        logger.error(f"Invalid or corrupted PDF: {str(e)}")
        raise PDFProcessingException(detail="Invalid or corrupted PDF")