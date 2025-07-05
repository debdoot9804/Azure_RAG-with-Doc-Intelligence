import os
from langchain.embeddings import OpenAIEmbeddings
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, VectorSearch,
    VectorSearchAlgorithmConfiguration, VectorField
)
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from backend.logger import setup_logger

logger = setup_logger()
VECTOR_DIMENSIONS = 1536  # adjust if using another model like text-embedding-3-large

# Get Embedding Model
def get_embed_model():
    return OpenAIEmbeddings(
        azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
        openai_api_key=os.getenv("AZURE_OPENAI_KEY"),
        openai_api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
        openai_api_version=os.getenv("AZURE_OPENAI_EMBEDDING_VERSION")
    )

# Create Azure Search Index (if it doesn't exist)
def create_azure_ai_search_index():
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    key = os.getenv("AZURE_SEARCH_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX")

    index_client = SearchIndexClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    existing_indexes = [i.name for i in index_client.list_indexes()]

    if index_name in existing_indexes:
        logger.info(f"Search index '{index_name}' already exists. Skipping creation.")
        return

    fields = [
        SimpleField(name="id", type="Edm.String", key=True),
        SimpleField(name="content", type="Edm.String", searchable=True),
        VectorField(name="content_vector", dimensions=VECTOR_DIMENSIONS, vector_search_configuration="vector-config")
    ]

    vector_search = VectorSearch(
        algorithm_configurations=[
            VectorSearchAlgorithmConfiguration(
                name="vector-config",
                kind="hnsw",
                hnsw_parameters={"m": 4, "efConstruction": 400, "efSearch": 500}
            )
        ]
    )

    index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search)
    index_client.create_index(index)
    logger.info(f"Search index '{index_name}' created successfully.")

# Generate Embeddings from Chunks
def generate_chunk_embeddings(chunks):
    embed_model = get_embed_model()
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

    search_client = SearchClient(endpoint=endpoint,
                                 index_name=index_name,
                                 credential=AzureKeyCredential(key))

    logger.info(f"Uploading {len(docs)} documents to Azure AI Search index '{index_name}'...")
    result = search_client.upload_documents(documents=docs)
    logger.info("Documents uploaded successfully.")
    return result

# Driver function for this
def create_embeddings_index(chunks):
    try:
        logger.info("Starting embedding + indexing pipeline...")
        create_azure_ai_search_index()
        docs = generate_chunk_embeddings(chunks)
        upload_documents_to_index(docs)
        logger.info("Embedding pipeline completed successfully.")
    except Exception as e:
        logger.error(f"Embedding/indexing pipeline failed: {e}")
        raise e
