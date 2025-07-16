from azure.storage.blob import BlobServiceClient
import os 
from backend.logger import setup_logger
from datetime import datetime, timedelta
from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from dotenv import load_dotenv
dotenv_path = os.path.join("E:\\agentic-genAI-project\\AZURE-RAG", "config", "settings.env")
if not os.path.exists(dotenv_path):
    raise FileNotFoundError(f"Environment file not found at {dotenv_path}")
load_dotenv(dotenv_path)
logger = setup_logger()

def upload_to_blob(file_path, container_name, blob_name):
    """
    Uploads file to Azure Blob Storage.
    """
    try:
        logger.info(f"Inputs: file_path={file_path}, container_name={container_name}, blob_name={blob_name}")
        if not all([file_path, container_name, blob_name]):
            raise ValueError(f"Invalid input: file_path={file_path}, container_name={container_name}, blob_name={blob_name}")
        
        connection_str = os.getenv("AZURE_BLOB_CONNECTION_STRING")
        logger.info(f"Connection string: {'Set' if connection_str else 'None'}")
        if not connection_str:
            raise ValueError("Azure Blob connection string not found")
        
        blob_service = BlobServiceClient.from_connection_string(connection_str)
        logger.info(f"Blob service account name: {blob_service.account_name}")
        
        blob_client = blob_service.get_blob_client(container=container_name, blob=blob_name)
        logger.info(f"Blob client URL: {blob_client.url}")
        
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        
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
        logger.info(f"Uploaded {blob_name} and generated SAS URL: {sas_url}")
        return sas_url
    
    except Exception as e:
        logger.error(f"Blob upload failed: {str(e)}")
        raise e