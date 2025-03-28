import os
import argparse
from blob_storage_client import BlobStorageClient

# Settings
CONTAINER_NAME = "minecraft"  # Azure Blob Storage container name
DOWNLOAD_FOLDER = "downloaded_images"  # Folder to store downloaded images
SUPPORTED_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']  # Supported image extensions

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Download all images from Azure Blob Storage container.')
    parser.add_argument('--container', type=str, default=CONTAINER_NAME, 
                        help=f'Container name (default: {CONTAINER_NAME})')
    parser.add_argument('--folder', type=str, default=DOWNLOAD_FOLDER, 
                        help=f'Download folder (default: {DOWNLOAD_FOLDER})')
    parser.add_argument('--all', action='store_true', 
                        help='Download all files, not just images')
    args = parser.parse_args()
    
    # Connect to Azure Blob Storage
    storage_client = BlobStorageClient(args.container)
    
    # Create download folder if it doesn't exist
    if not os.path.exists(args.folder):
        os.makedirs(args.folder)
        print(f"Created download folder: {args.folder}")
    
    # Get the list of all files in the container
    blob_list = storage_client.list_blobs()
    
    if not blob_list:
        print(f"No files found in container '{args.container}'.")
        return
    
    total_files = len(blob_list)
    print(f"Found {total_files} files in container '{args.container}'.")
    
    # Filter for image files if --all flag is not set
    if not args.all:
        blob_list = [blob for blob in blob_list if any(
            blob.name.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS)]
        print(f"Filtered to {len(blob_list)} image files.")
    
    # Get the container client
    container_client = storage_client.blob_service_client.get_container_client(storage_client.container_name)
    
    # Download each file
    for i, blob in enumerate(blob_list, 1):
        try:
            # Prepare local filename
            local_path = os.path.join(args.folder, os.path.basename(blob.name))
            
            # Check if file exists and has the same size
            if os.path.exists(local_path) and os.path.getsize(local_path) == blob.size:
                print(f"Skipping {i} of {len(blob_list)}: {blob.name} (already exists)")
                continue
                
            # Download blob content
            blob_client = container_client.get_blob_client(blob.name)
            with open(local_path, 'wb') as file:
                blob_data = blob_client.download_blob().readall()
                file.write(blob_data)
            
            print(f"Downloaded {i} of {len(blob_list)}: {blob.name}")
        except Exception as e:
            print(f"Error downloading {blob.name}: {e}")
    
    print(f"Download complete. Files saved to {args.folder}")

if __name__ == "__main__":
    main()
