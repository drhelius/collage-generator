import io
import math
from PIL import Image
from blob_storage_client import BlobStorageClient

# Settings
CONTAINER_NAME = "images"  # Azure Blob Storage container name
OUTPUT_SIZE = (2048, 2048)  # Output collage size in pixels
OUTPUT_FILENAME = "collage4.png"  # Output filename
RESIZE_ALGORITHM = Image.Resampling.LANCZOS  # Resampling algorithm for resizing

def calculate_grid_size(num_images):
    """Calculate the optimal grid dimensions for the collage."""
    grid_size = int(math.sqrt(num_images))
    return grid_size

def main():
    # Connect to Azure Blob Storage
    storage_client = BlobStorageClient(CONTAINER_NAME)
    
    # Get the list of all files in the container
    blob_list = storage_client.list_blobs()
    
    # Filter for PNG files
    png_blobs = [blob for blob in blob_list if blob.name.lower().endswith('.png')]
    
    if not png_blobs:
        print("No PNG files found in the container.")
        return
    
    print(f"Found {len(png_blobs)} PNG files.")
    
    # Calculate grid size
    grid_size = calculate_grid_size(len(png_blobs))
    print(f"Creating a {grid_size}x{grid_size} grid collage.")
    
    # Limit blobs to what fits in the grid
    total_images = min(len(png_blobs), grid_size * grid_size)
    selected_blobs = png_blobs[:total_images]
    
    # Create a new blank image for the collage
    collage = Image.new('RGBA', OUTPUT_SIZE, (255, 255, 255, 255))
    
    # Calculate thumbnail size
    thumb_width = OUTPUT_SIZE[0] // grid_size
    thumb_height = OUTPUT_SIZE[1] // grid_size
    
    # Get the container client once
    container_client = storage_client.blob_service_client.get_container_client(storage_client.container_name)
    
    # Process one image at a time
    for i, blob in enumerate(selected_blobs, 1):
        try:
            # Download blob content using the container client
            blob_client = container_client.get_blob_client(blob.name)
            blob_data = blob_client.download_blob().readall()
            
            # Convert bytes to image
            with Image.open(io.BytesIO(blob_data)) as image:
                # Calculate position in the grid
                x = ((i-1) % grid_size) * thumb_width
                y = ((i-1) // grid_size) * thumb_height
                
                # Resize the image to fit in the grid
                thumb = image.resize((thumb_width, thumb_height), RESIZE_ALGORITHM)
                
                # Paste the thumbnail into the collage
                collage.paste(thumb, (x, y))
                
                print(f"Processed {i} of {total_images}: {blob.name}")
        except Exception as e:
            print(f"Error processing {blob.name}: {e}")
    
    # Save the collage locally
    collage.save(OUTPUT_FILENAME)
    print(f"Collage saved to {OUTPUT_FILENAME}")

if __name__ == "__main__":
    main()
