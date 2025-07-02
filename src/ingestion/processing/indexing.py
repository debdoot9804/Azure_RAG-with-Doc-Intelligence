from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient

def create_index(index_name, endpoint, key):
    client = SearchIndexClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    # Define your index schema
    index_schema = {
        "name": index_name,
        "fields": [
            {"name": "id", "type": "Edm.String", "key": True},
            {"name": "content", "type": "Edm.String", "searchable": True}
        ]
    }
    client.create_index(index_schema)

def index_chunks(index_name, endpoint, key, chunks):
    client = SearchClient(endpoint=endpoint, index_name=index_name, credential=AzureKeyCredential(key))
    for i, chunk in enumerate(chunks):
        client.upload_document({"id": str(i), "content": chunk})    