import os
from dotenv import load_dotenv
load_dotenv()

from openai import AzureOpenAI 
from azure.search.documents.indexes import SearchIndexClient
# from azure.search.documents.indexes.models import (
#     SearchIndex,
#     SearchFieldDataType,
#     SearchField,
#     VectorSearch,
#     VectorSearchAlgorithmConfiguration,
#     SearchableField
# )
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import requests
import json
from backend.vectordb import get_azure_ai_search
from backend.logger import setup_logger

logger = setup_logger()
VECTOR_DIMENSIONS = 1536  # embedding dimesnion size for text-embedding-3-small

from backend.embed_model import AzureEmbedder


# Create Azure Search Index (if it doesn't exist)
# def create_azure_ai_search_index():
#     """Create an Azure AI Search index for storing embeddings."""

#     logger.info("Creating Azure AI Search index...")

#     search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
#     search_key = os.getenv("AZURE_SEARCH_KEY")
#     index_name = os.getenv("AZURE_SEARCH_INDEX")
#     vector_dimensions = 1536  

#     # url = f"{search_endpoint}/indexes/{index_name}?api-version=2024-03-01-Preview"
#     search_client = SearchIndexClient(search_endpoint, AzureKeyCredential(search_key), api_version="2023-10-01-preview")

#     headers = {
#         "Content-Type": "application/json",
#         "api-key": search_key
#     }

#     index_schema = {
#         "name": index_name,
#         "fields": [
#             {
#                 "name": "id",
#                 "type": "Edm.String",
#                 "key": True,
#                 "filterable": True,
#             },
#             {
#                 "name": "content",
#                 "type": "Edm.String",
#                 "searchable": True
#             },
#             {
#                 "name": "content_vector",
#                 "type": "Collection(Edm.Single)",
#                 "searchable": False,
#                 "filterable": False,
#                 "sortable": False,
#                 "facetable": False,
#                 "dimensions": 1536,
#                 "vectorSearchConfiguration": "vector-config"
#             }
#         ],
#         "vectorSearch": {
#             "algorithmConfigurations": [
#                 {
#                     "name": "vector-config",
#                     "kind": "hnsw",
#                     "hnswParameters": {
#                         "m": 4,
#                         "efConstruction": 400
#                     }
#                 }
#             ]
#         }
#     }

#     try:
#         response = requests.put(search_client, headers=headers, json=index_schema)
#         if response.status_code in [200, 201]:
#             logger.info(f" Index '{index_name}' created successfully via REST API.")
#         else:
#             logger.error(f" Failed to create index: {response.status_code} {response.text}")
#     except Exception as e:
#         logger.error(f"Exception during index creation: {e}")

# Generate Embeddings from Chunks

from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    VectorSearchAlgorithmConfiguration,
    HnswParameters
)


def generate_chunk_embeddings(chunks):
    embed_model = AzureEmbedder()
    logger.info("Generating embeddings for all text chunks...")

    docs = []
    for i, chunk in enumerate(chunks):
        embeddings = embed_model.embed_query(chunk)
        docs.append({
            "id": str(i),
            "content": chunk,
            "content_vector":embeddings
        })

    logger.info(f"Generated embeddings for {len(chunks)} chunks.")
    return docs

# Upload Documents to Azure AI Search
def upload_documents_to_index(docs):
    index_name = os.getenv("AZURE_SEARCH_INDEX")
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    key = os.getenv("AZURE_SEARCH_KEY")

    search_client = get_azure_ai_search()   

    logger.info(f"Uploading {len(docs)} documents to Azure AI Search index '{index_name}'...")
    result = search_client.upload_documents(documents=docs)
    logger.info("Documents uploaded successfully.")
    return result

# Driver function for this
def create_embeddings_index(chunks):
    try:
        logger.info("Starting embedding + indexing pipeline...")
        #create_azure_ai_search_index()
        docs = generate_chunk_embeddings(chunks)
        upload_documents_to_index(docs)
        logger.info("Embedding pipeline completed successfully.")
    except Exception as e:
        logger.error(f"Embedding/indexing pipeline failed: {e}")
        raise e
