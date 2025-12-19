from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.modules.document.exceptions import TextSplittingException
import logging

logger = logging.getLogger(__name__)

def split_text(text:str) ->list[str]:
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 2048, # 512 tokens 
            chunk_overlap=80, # 4% overlap
            separators=[
                "\n\n",
                "\n",
                ". ",
                " "
            ]
        )
        return text_splitter.split_text(text)
    except Exception as e:
        logger.error(f"Failed to split text: {e}")
        raise TextSplittingException(
            detail = "invalid characters"
        )