import base64
from app.modules.document.exceptions import PDFProcessingException
import logging
import pymupdf
import re
import gc  

logger = logging.getLogger(__name__)


def extract_text_from_pdf(content: bytes) -> str:
    doc = None  
    try:
        content_bytes = base64.b64decode(content)
        doc = pymupdf.open(stream=content_bytes, filetype="pdf")
        pages = []
        
        for page_num in range(len(doc)):
            try:
                page = doc[page_num]
                page_string = str(page.get_text())
                
                # clean vulnerable bytes
                page_string = page_string.replace('\x00', '')
                page_string = page_string.replace('\ufffd', '')
                page_string = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', page_string)
                
                # handle excessive whitespace
                page_string = re.sub(r'\n{3,}', '\n\n', page_string)
                page_string = re.sub(r' {2,}', ' ', page_string)
                
                # only append pages with valid content
                if page_string.strip():
                    pages.append(page_string)
                else:
                    logger.warning(f"Page {page_num + 1} is empty after cleanup")
                    
            except Exception as e:
                # only skip the page where the error occures 
                logger.error(f"Error extracting page {page_num + 1}: {e}")
                continue
        
        content_str = "\n\n".join(pages)
        
        logger.info(f"Extracted text length: {len(content_str)}")
        logger.info(f"First 200 chars: {content_str[:200]}")
        logger.info(f"Pages processed: {len(pages)}/{len(doc)}")
        
        return content_str
        
    except Exception as e:
        logger.error(f"Invalid or corrupted PDF: {str(e)}")
        raise PDFProcessingException(detail="Invalid or corrupted PDF")
    
    finally:
        # close document and clear ram
        if doc is not None:
            doc.close()
        del content_bytes
        gc.collect()  
