import base64
import gc
import logging
import re
import unicodedata
import pymupdf
from worker.document.document_repository import DocumentRepositorySync
from worker.document.exceptions import PDFProcessingException, TextSplittingException
from langchain_text_splitters import RecursiveCharacterTextSplitter
import psutil
import os

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self, repository:DocumentRepositorySync):
        self.repository = repository

    def extract_text_from_pdf(self, content: str) -> str:
        doc = None
        try:
            content_bytes = base64.b64decode(content, validate=True)
            doc = pymupdf.open(stream=content_bytes, filetype="pdf")
            pages = []

            for page_num in range(len(doc)):
                try:
                    page = doc.load_page(page_num)
                    page_string = str(page.get_text())
                    page_string = page_string.replace("\x00", "")
                    page_string = page_string.replace("\ufffd", "")
                    page_string = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", page_string)
                    page_string = re.sub(r"\n{3,}", "\n\n", page_string)
                    page_string = re.sub(r" {2,}", " ", page_string)
                    if page_string.strip():
                        pages.append(page_string)
                    else:
                        logger.warning(f"Page {page_num + 1} is empty after cleanup")
                except Exception as e:
                    logger.error(f"Error extracting page {page_num + 1}: {e}")
                    continue

            content_str = "\n\n".join(pages)
            content_str = unicodedata.normalize("NFKC", content_str)
            content_str = re.sub("[\u200E\u200F\u202A-\u202E\u2066-\u2069]", "", content_str)

            if len(content_str) > 5_000_000:
                raise PDFProcessingException(detail="Extracted text exceeds size limit")

            logger.info(f"Extracted text length: {len(content_str)}")
            return content_str

        except Exception as e:
            logger.error(f"Invalid or corrupted PDF: {str(e)}")
            raise PDFProcessingException(detail="Invalid or corrupted PDF")

        finally:
            if doc is not None:
                doc.close()
            gc.collect()


    def log_memory(self, step_name: str) -> float:
        process = psutil.Process(os.getpid())
        mem_mb = process.memory_info().rss / 1024 / 1024
        logger.info(f"📊 MEMORY [{step_name}]: {mem_mb:.2f} MB")
        return mem_mb

    def split_text(self, text: str) -> list[str]:
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=2048,
                chunk_overlap=100,
                separators=["\n\n", "\n", ". ", " "],
            )
            chunks = text_splitter.split_text(text)
            clean_chunks = []
            for i, chunk in enumerate(chunks):
                try:
                    chunk.encode("utf-8")
                except UnicodeEncodeError as e:
                    logger.error(f"Chunk {i} has encoding issues: {e}, attempting cleanup")
                    chunk = chunk.encode("utf-8", errors="ignore").decode("utf-8")
                if chunk.strip():
                    clean_chunks.append(chunk.strip())
                else:
                    logger.warning(f"Chunk {i} is empty, skipping")
            logger.info(f"Split into {len(clean_chunks)} chunks (from {len(chunks)} raw chunks)")
            return clean_chunks
        except Exception as e:
            logger.error(f"Failed to split text: {e}")
            raise TextSplittingException(detail="invalid characters")
