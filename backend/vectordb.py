from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv
load_dotenv()
from backend.logger import setup_logger

logger = setup_logger()

def get_azure_ai_search():
    """ For getting Azure AI search vectordb"""

    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    key = os.getenv("AZURE_SEARCH_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX")

    return SearchClient(endpoint=endpoint,
                        index_name=index_name,
                        credential=AzureKeyCredential(key))
