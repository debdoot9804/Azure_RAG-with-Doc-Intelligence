import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration
)
from backend.logger import setup_logger
from backend.vectordb import get_azure_ai_search
from backend.embed_model import AzureEmbedder

# Load environment variables
dotenv_path = os.path.join("E:\\agentic-genAI-project\\AZURE-RAG", "config", "settings.env")
if not os.path.exists(dotenv_path):
    raise FileNotFoundError(f"Environment file not found at {dotenv_path}")
load_dotenv(dotenv_path)

logger = setup_logger()
VECTOR_DIMENSIONS = 1536  # Embedding dimension size for text-embedding-3-small

def clear_search_index(index_name=None):
    """
    Clears all documents from the Azure AI Search index.
    """
    try:
        search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        search_key = os.getenv("AZURE_SEARCH_KEY")
        index_name = index_name or os.getenv("AZURE_SEARCH_INDEX")
        
        if not all([search_endpoint, search_key, index_name]):
            raise ValueError("Azure AI Search endpoint, key, or index name not found")
        
        search_client = SearchClient(endpoint=search_endpoint, index_name=index_name, credential=AzureKeyCredential(search_key))
        
        # Delete all documents in the index
        results = search_client.search(search_text="*", select="id")
        documents = [{"id": doc["id"]} for doc in results]
        if documents:
            search_client.delete_documents(documents)
            logger.info(f"Cleared {len(documents)} documents from Azure AI Search index '{index_name}'")
        else:
            logger.info(f"No documents to clear in Azure AI Search index '{index_name}'")
    except Exception as e:
        logger.error(f"Failed to clear search index '{index_name}': {str(e)}")
        raise e


def create_azure_ai_search_index(index_name=None):
    logger.info("Checking/Creating Azure AI Search index...")
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    search_key = os.getenv("AZURE_SEARCH_KEY")
    index_name = index_name or os.getenv("AZURE_SEARCH_INDEX")
    vector_dimensions = VECTOR_DIMENSIONS

    if not all([search_endpoint, search_key, index_name]):
        raise ValueError("Azure AI Search endpoint, key, or index name not found")

    search_client = SearchIndexClient(search_endpoint, AzureKeyCredential(search_key))

    # Check if index exists
    try:
        existing_index = search_client.get_index(index_name)
        logger.info(f"Index '{index_name}' already exists, skipping creation.")
        return
    except Exception:
        logger.info(f"Index '{index_name}' does not exist, creating new index.")

    # Define the index schema
    fields = [
        SearchField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
        SearchField(name="content", type=SearchFieldDataType.String, searchable=True),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=vector_dimensions,
            vector_search_profile_name="vector-config"
        )
    ]

    vector_search = VectorSearch(
        profiles=[VectorSearchProfile(name="vector-config", algorithm_configuration_name="vector-config")],
        algorithms=[HnswAlgorithmConfiguration(name="vector-config")]
    )

    index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search)

    try:
        search_client.create_index(index)
        logger.info(f"Index '{index_name}' created successfully.")
    except Exception as e:
        logger.error(f"Failed to create index '{index_name}': {str(e)}")
        raise e
    
def generate_chunk_embeddings(chunks):
    # """
    # Generate embeddings for all text chunks using AzureEmbedder.
    # """
    # embed_model = AzureEmbedder()
    # logger.info("Generating embeddings for all text chunks...")

    # docs = []
    # for i, chunk in enumerate(chunks):
    #     embeddings = embed_model.embed_query(chunk)
    #     docs.append({
    #         "id": str(i),
    #         "content": chunk,
    #         "content_vector": embeddings
    #     })

    # logger.info(f"Generated embeddings for {len(chunks)} chunks.")
    # return docs

    embed_model = AzureEmbedder()
    logger.info("Generating embeddings for all text chunks...")
    docs = []
    # Batch chunks (e.g., up to 16 per request, adjust based on Azure OpenAI limits)
    batch_size = 16
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        embeddings = embed_model.embed_batch(batch)  # Hypothetical batch method
        for j, embedding in enumerate(embeddings):
            docs.append({
                "id": str(i + j),
                "content": batch[j],
                "content_vector": embedding
            })
    logger.info(f"Generated embeddings for {len(chunks)} chunks.")
    return docs

def upload_documents_to_index(docs, index_name=None):
    """
    Upload documents to Azure AI Search index.
    """
    index_name = index_name or os.getenv("AZURE_SEARCH_INDEX")
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    key = os.getenv("AZURE_SEARCH_KEY")

    if not all([endpoint, key, index_name]):
        raise ValueError("Azure AI Search endpoint, key, or index name not found")

    search_client = get_azure_ai_search()

    logger.info(f"Uploading {len(docs)} documents to Azure AI Search index '{index_name}'...")
    result = search_client.upload_documents(documents=docs)
    logger.info("Documents uploaded successfully.")
    return result

def create_embeddings_index(chunks, index_name=None):
    """
    Creates or updates an Azure AI Search index with embeddings for the provided chunks.
    Deletes and recreates the index to avoid schema conflicts.
    """
    try:
        logger.info("Starting embedding + indexing pipeline...")
        index_name = index_name or os.getenv("AZURE_SEARCH_INDEX")
        
        # Create or recreate the index
        create_azure_ai_search_index(index_name)
        
        # Generate and upload embeddings
        docs = generate_chunk_embeddings(chunks)
        upload_documents_to_index(docs, index_name)
        logger.info("Embedding pipeline completed successfully.")
    except Exception as e:
        logger.error(f"Embedding/indexing pipeline failed: {str(e)}")
        raise e