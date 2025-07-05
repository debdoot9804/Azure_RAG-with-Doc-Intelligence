from langchain.text_splitter import RecursiveCharacterTextSplitter
from backend.logger import setup_logger

logger=setup_logger()

def chunk_text(text):
    try:
        splitter=RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=50)
        chunks=splitter.split_text(text)
        logger.info(f"Text chunking complete. {len(chunks)} chunks created.")
        return chunks
    except Exception as e:
        logger.error(f"Text chunking failed: {e}")
        raise e
    