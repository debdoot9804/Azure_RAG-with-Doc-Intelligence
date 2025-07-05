import os
import backend.logger import setup_logger

logger = setup_logger()

def get_ai_search_client():
    """ For Azure AI Search client """
    endpoint=os.getnev()