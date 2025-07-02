# src/main.py
import os
import logging
from dotenv import load_dotenv
from utils.logging_setup import setup_logging
from ingestion.blob_upload import upload_pdf_to_blob_storage
from ingestion.document_processing import analyze_pdf
from processing.chunking import chunk_document
from processing.indexing import create_index, index_chunks

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

def main():
    # Load configuration from environment variables
    config = {
        "blob_connection_string": os.getenv("BLOB_CONNECTION_STRING"),
        "blob_container_name": os.getenv("BLOB_CONTAINER_NAME"),
        "blob_account_name": os.getenv("BLOB_ACCOUNT_NAME"),
        "pdf_file_path": os.getenv("PDF_FILE_PATH"),
        "document_intelligence_endpoint": os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT"),
        "document_intelligence_key": os.getenv("DOCUMENT_INTELLIGENCE_KEY"),
        "search_endpoint": os.getenv("SEARCH_ENDPOINT"),
        "search_key": os.getenv("SEARCH_KEY"),
        "index_name": os.getenv("INDEX_NAME")
    }

    # Upload PDF to Blob Storage
    upload_pdf_to_blob_storage(config['blob_connection_string'], config['blob_container_name'], config['pdf_file_path'])

    # Analyze PDF with Document Intelligence
    blob_url = f"https://{config['blob_account_name']}.blob.core.windows.net/{config['blob_container_name']}/{config['pdf_file_path'].split('/')[-1]}"
    document_text = analyze_pdf(config['document_intelligence_endpoint'], config['document_intelligence_key'], blob_url)

    # Chunk the document
    chunks = chunk_document(document_text)

    # Create index and index chunks
    create_index(config['index_name'], config['search_endpoint'], config['search_key'])
    index_chunks(config['index_name'], config['search_endpoint'], config['search_key'], chunks)

if __name__ == "__main__":
    main()
