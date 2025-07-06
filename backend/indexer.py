# backend/index_manager.py

import os
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    VectorSearch,
    VectorSearchAlgorithmConfiguration,
    VectorField
)
from azure.core.credentials import AzureKeyCredential
from backend.logger import setup_logger

logger = setup_logger()
VECTOR_DIMENSIONS = 1536

def create_vector_index():
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    key = os.getenv("AZURE_SEARCH_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX")

    client = SearchIndexClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    logger.info(f"Creating or updating index '{index_name}' with vector search...")

    fields = [
        SimpleField(name="id", type="Edm.String", key=True, filterable=True),
        SearchableField(name="content", type="Edm.String"),
        VectorField(
            name="content_vector",
            dimensions=VECTOR_DIMENSIONS,
            vector_search_configuration="vector-config"
        )
    ]

    vector_config = VectorSearch(
        algorithm_configurations=[
            VectorSearchAlgorithmConfiguration(
                name="vector-config",
                kind="hnsw",
                hnsw_parameters={"m": 4, "efConstruction": 400}
            )
        ]
    )

    index = SearchIndex(
        name=index_name,
        fields=fields,
        vector_search=vector_config
    )

    client.create_or_update_index(index)
    logger.info(f"✅ Vector index '{index_name}' created successfully.")
