from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

class BlobStorageClient:
    def __init__(self, container_name):
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_name = container_name
        
        self.account_name = None
        self.account_key = None
        
        conn_dict = {
            item.split('=', 1)[0]: item.split('=', 1)[1]
            for item in connection_string.split(';')
            if '=' in item
        }
        
        self.account_name = conn_dict.get('AccountName')
        self.account_key = conn_dict.get('AccountKey')
        
        container_client = self.blob_service_client.get_container_client(self.container_name)
        if not container_client.exists():
            container_client.create_container()

    def upload_file(self, local_file_path, blob_name=None):
        try:
            blob_name = blob_name or os.path.basename(local_file_path)
            blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=blob_name)
            with open(local_file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
                print(f"Uploaded {blob_name} to Azure Blob Storage.")
        except Exception as e:
            print(f"Failed to upload {local_file_path} to Azure Blob Storage: {e}")
            raise e
    
    def upload_bytes(self, bytes_data, blob_name):
        try:
            blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=blob_name)
            # Reset pointer to start of stream
            bytes_data.seek(0)
            blob_client.upload_blob(bytes_data, overwrite=True)
            print(f"Uploaded {blob_name} to Azure Blob Storage.")
        except Exception as e:
            print(f"Failed to upload bytes to Azure Blob Storage: {e}")
            raise e

    def download_file(self, blob_name, download_file_path):
        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=blob_name)
        with open(download_file_path, "wb") as file:
            download_stream = blob_client.download_blob()
            file.write(download_stream.readall())
            print(f"Downloaded {blob_name} to {download_file_path}.")

    def get_blob_url(self, blob_name, sas_token=True, expiry_hours=1):
        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=blob_name)
        
        if not sas_token:
            return blob_client.url
        
        try:
            # Generate SAS token with read permission
            sas_token = generate_blob_sas(
                account_name=self.account_name,
                container_name=self.container_name,
                blob_name=blob_name,
                account_key=self.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
            )
            
            # Return the URL with the SAS token
            return f"{blob_client.url}?{sas_token}"
        except Exception as e:
            print(f"Failed to generate SAS token: {e}")
            # Fall back to the regular URL without SAS token
            return blob_client.url

    def list_blobs(self):
        """List all blobs in the container."""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            blobs = list(container_client.list_blobs())
            return blobs
        except Exception as e:
            print(f"Failed to list blobs in container {self.container_name}: {e}")
            raise e
