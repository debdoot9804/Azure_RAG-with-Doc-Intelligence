from azure.storage.blob import BlobServiceClient
import os 
from backend.logger import setup_logger

logger=setup_logger()

def upload_to_blob(file_path,container_name,blob_name):
    """
    Uploads file to Azure Blob Storage."""
    try:
        connection_str=ps.getenv("AZURE_BLOB_CONNECTION_STRING")
        blob_service=BlobServiceClient.from_connection_string(connection_str)
        blob_client=blob_service.get_blob_client(container=container_name, blob=blob_name)

        with open(file_path,"rb") as data:
            blob_client.upload_blob(data,overwrite=True)

        logger.info(f"File {file_path} uploaded to blob {blob_name} in container {container_name}.")
        return blob_client.url
    except Exception as e:    
        logger.error(f"Blob upload failed :{e}")
        raise e
