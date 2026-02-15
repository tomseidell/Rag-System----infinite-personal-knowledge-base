from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.modules.document.exceptions import TextSplittingException
import logging

logger = logging.getLogger(__name__)

def split_text(text: str) -> list[str]:
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2048,  
            chunk_overlap=100,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " "
            ]
        )
        
        chunks = text_splitter.split_text(text)
        
        # validating chunks 
        clean_chunks = []
        for i, chunk in enumerate(chunks):
            # check for encoding errors
            try:
                chunk.encode('utf-8')
            except UnicodeEncodeError as e:
                logger.error(f"Chunk {i} has encoding issues: {e}, attempting cleanup")
                chunk = chunk.encode('utf-8', errors='ignore').decode('utf-8')
            
            # only add not empy chunks
            if chunk.strip():
                clean_chunks.append(chunk.strip())
            else:
                logger.warning(f"Chunk {i} is empty, skipping")
        
        logger.info(f"Split into {len(clean_chunks)} chunks (from {len(chunks)} raw chunks)")
        return clean_chunks
        
    except Exception as e:
        logger.error(f"Failed to split text: {e}")
        raise TextSplittingException(detail="invalid characters")
