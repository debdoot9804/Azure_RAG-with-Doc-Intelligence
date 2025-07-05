from azure.storage.blob import BlobServiceClient
import os 
from backend.logger import setup_logger
from datetime import datetime, timedelta
from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from dotenv import load_dotenv
load_dotenv()
logger=setup_logger()

def upload_to_blob(file_path,container_name,blob_name):
    """
    Uploads file to Azure Blob Storage."""
    try:
        connection_str=os.getenv("AZURE_BLOB_CONNECTION_STRING")
        blob_service=BlobServiceClient.from_connection_string(connection_str)
        blob_client=blob_service.get_blob_client(container=container_name, blob=blob_name)

        with open(file_path,"rb") as data:
            blob_client.upload_blob(data,overwrite=True)

        # Generate a SAS URL for Document Intelligence to access the blob
        sas_token = generate_blob_sas(
            account_name=blob_service.account_name,
            container_name=container_name,
            blob_name=blob_name,
            account_key=blob_service.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(minutes=30)
        )

        sas_url = f"{blob_client.url}?{sas_token}"

        logger.info(f"Uploaded {blob_name} and generated SAS URL.")
        return sas_url

    except Exception as e:    
        logger.error(f"Blob upload failed :{e}")
        raise e
