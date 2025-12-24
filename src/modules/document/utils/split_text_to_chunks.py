from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.modules.document.exceptions import TextSplittingException
import logging

logger = logging.getLogger(__name__)

def split_text(text: str) -> list[str]:
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2048,  # Reduziert von 1900 für mehr Sicherheit
            chunk_overlap=100,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " "
            ]
        )
        
        chunks = text_splitter.split_text(text)
        
        # Validierung und Cleanup der Chunks
        clean_chunks = []
        for i, chunk in enumerate(chunks):
            # Prüfe auf problematische Chunks
            if len(chunk) > 2000:
                logger.warning(f"Chunk {i} is too long ({len(chunk)} chars), splitting further")
                # Split zu große Chunks nochmal
                sub_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
                sub_chunks = sub_splitter.split_text(chunk)
                clean_chunks.extend(sub_chunks)
                continue
            
            # Prüfe auf Encoding-Probleme
            try:
                chunk.encode('utf-8')
            except UnicodeEncodeError as e:
                logger.error(f"Chunk {i} has encoding issues: {e}, attempting cleanup")
                chunk = chunk.encode('utf-8', errors='ignore').decode('utf-8')
            
            # Nur nicht-leere Chunks hinzufügen
            if chunk.strip():
                clean_chunks.append(chunk.strip())
            else:
                logger.warning(f"Chunk {i} is empty, skipping")
        
        logger.info(f"Split into {len(clean_chunks)} chunks (from {len(chunks)} raw chunks)")
        return clean_chunks
        
    except Exception as e:
        logger.error(f"Failed to split text: {e}")
        raise TextSplittingException(detail="invalid characters")
