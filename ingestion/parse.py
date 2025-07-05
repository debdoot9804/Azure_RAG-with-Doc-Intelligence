from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import os
from backend.logger import setup_logger
from dotenv import load_dotenv
load_dotenv()

logger = setup_logger()
def parse_document(blob_url):
    """
    Parses a document from Azure Blob Storage using document intelligence
    """
    try:
        endpoint=os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
        key=os.getenv("AZURE_FORM_RECOGNIZER_KEY")

        client= DocumentAnalysisClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )
        poller = client.begin_analyze_document_from_url(
            "prebuilt-layout", blob_url
        )
        result = poller.result()

        extracted_text="\n".join([line.content for page in result.pages for line in page.lines])
        logger.info("Text extraction complete")
        return extracted_text
    except Exception as e:
        logger.error(f"Document parsing failed: {e}")
        raise e
    
    

