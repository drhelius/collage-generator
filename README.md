# Image Collage Generator

This project creates a collage from PNG images stored in Azure Blob Storageges.

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure Azure Blob Storage:
   - Copy `.env.sample` to `.env`
   - Update `.env` with your Azure Storage connection string

## Usage

### Generate a Collage

1. Update settings in `collage_generator.py` if needed:
   - `CONTAINER_NAME`: The Azure Blob Storage container to get images from
   - `OUTPUT_SIZE`: The size of the final collage (default: 1024x1024)
   - `OUTPUT_FILENAME`: The name of the generated collage file
   - `RESIZE_ALGORITHM`: The algorithm used for resizing images

2. Run the script:
   ```
   python collage_generator.py
   ```

### Download All Images

To download all images from a container:

```
python download_images.py
```

Options:
- `--container NAME`: Specify a different container (default: minecraft)
- `--folder PATH`: Specify a different download folder (default: downloaded_images)
- `--all`: Download all files, not just images
