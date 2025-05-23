import os
import aiofiles
from fastapi import UploadFile
from typing import Literal


async def save_upload_file(upload_file: UploadFile, point_id: str, collection: Literal['wardrobe', 'marketplace']) -> str:
    """
    Save an uploaded file to the static directory
    
    Args:
        upload_file: The uploaded file
        point_id: The point ID to use as filename
    
    Returns:
        The relative path to the saved file
    """
    # Reset file pointer to beginning
    await upload_file.seek(0)
    
    # Create file path
    file_extension = os.path.splitext(upload_file.filename)[1]
    directory = "app/static/images-qdrant"
    file_path = f"{directory}/{collection}/{point_id}{file_extension}"
    
    # Ensure directory exists
    os.makedirs(directory, exist_ok=True)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await upload_file.read()
        await out_file.write(content)
    
    # Return relative path for storage/retrieval
    return f"app/static/images-qdrant/{collection}/{point_id}{file_extension}"