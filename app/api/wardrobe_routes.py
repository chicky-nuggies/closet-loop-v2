from fastapi import APIRouter, UploadFile, File, HTTPException, Form, status, Depends, BackgroundTasks

import uuid
import traceback

from app.models.schemas import ClothingItem
from app.dependencies import get_wardrobe_db
from app.services.vector_db import VectorDatabase
from app.utils.file_utils import save_upload_file
from app.utils.logging import logger

router = APIRouter()

# Storage for tracking upload status
upload_tasks = {}

@router.post('/upload-clothing')
async def upload_clothing(
    name: str = Form(...),
    category: str = Form(...),
    file: UploadFile = File(...),
    vector_db: VectorDatabase = Depends(get_wardrobe_db)
):
    try:
        logger.info("Received Image")
        # Generate a unique ID
        item_id = str(uuid.uuid4())
        
        # Save the file first
        image_path = await save_upload_file(file, item_id, 'wardrobe')
        
        # Process directly instead of using background tasks
        with open(image_path, "rb") as f:
            point_id = vector_db.upload_clothing(f, name, category, item_id)
        
        return {
            "id": item_id,
            "status": "completed",
            "name": name,
            "category": category,
            "image_path": image_path,
            "vector_id": point_id,
            "message": "Upload completed successfully."
        }
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error in upload_clothing: {str(e)}\n{error_details}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.get('/wardrobe')
async def get_wardrobe(
    vector_db: VectorDatabase = Depends(get_wardrobe_db),
):
    try:
        wardrobe_items = vector_db.retrieve_collection()
        return {
            "items": wardrobe_items
        }
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error in upload_clothing: {str(e)}\n{error_details}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

# @router.post('/upload-clothing')
# async def upload_clothing(
#     background_tasks: BackgroundTasks,
#     name: str = Form(...),
#     category: str = Form(...),
#     file: UploadFile = File(...),
#     vector_db: VectorDatabase = Depends(get_wardrobe_db)
# ):
#     try:
#         logger.info("Receive Image")
#         # Generate a unique ID for tracking
#         task_id = str(uuid.uuid4())
        
#         # Save the file first (this is usually quick)
#         image_path = await save_upload_file(file, task_id)
        
#         # Initialize task status
#         upload_tasks[task_id] = {
#             "status": "processing",
#             "name": name,
#             "category": category,
#             "image_path": image_path
#         }
        
#         # Define the background task inline with a lambda function
#         # This directly calls vector_db.upload_clothing and handles the status updates
#         background_tasks.add_task(
#             lambda: update_vector_db(task_id, image_path, name, category, vector_db)
#         )
        
#         # Return immediately with the tracking ID
#         return {
#             "id": task_id,
#             "status": "processing",
#             "name": name,
#             "category": category,
#             "image_path": image_path,
#             "message": "Upload started. Check status endpoint for completion."
#         }
#     except Exception as e:
#         error_details = traceback.format_exc()
#         print(f"Error in upload_clothing: {str(e)}\n{error_details}")
        
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred: {str(e)}"
#         )

@router.get('/upload-status/{task_id}')
async def get_upload_status(task_id: str):
    if task_id not in upload_tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload task not found"
        )
    
    return upload_tasks[task_id]

@router.delete('/delete-clothing/{clothing_id}')
async def delete_clothing(
    clothing_id: str,
    vector_db: VectorDatabase = Depends(get_wardrobe_db)
):
    try:
        # Call the delete_clothing method from VectorDatabase
        vector_db.delete_clothing(clothing_id)
        
        return {
            "success": True,
            "id": clothing_id,
            "message": "Clothing item deleted"
        }
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error deleting clothing: {str(e)}\n{error_details}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )





# Helper function for the background task
def update_vector_db(task_id: str, file_path: str, name: str, category: str, vector_db: VectorDatabase):
    try:
        logger.info('Starting Vector DB Upsert')
        # Open the file from the saved path
        with open(file_path, "rb") as f:
            # Process the vector DB operation - this is where the time-consuming work happens
            point_id = vector_db.upload_clothing(f, name, category, task_id)
        
        # Update status to completed
        upload_tasks[task_id]["status"] = "completed"
        upload_tasks[task_id]["vector_id"] = point_id
    except Exception as e:
        # Update status to failed
        upload_tasks[task_id]["status"] = "failed"
        upload_tasks[task_id]["error"] = str(e)
        print(f"Background task error: {str(e)}")


