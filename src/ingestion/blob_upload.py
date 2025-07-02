import logging
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger(__name__)

def upload_pdf_to_blob_storage(connection_string, container_name, file_path):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_path.split("/")[-1])

    with open(file_path, "rb") as data:
        logger.info(f"Uploading {file_path} to blob storage...")
        blob_client.upload_blob(data, overwrite=True)
        logger.info(f"Uploaded {file_path} to blob storage.")

