from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
import traceback

from app.services.vector_db import VectorDatabase
from app.dependencies import get_marketplace_db
from app.models.schemas import MarketplaceItem
from app.utils.file_utils import save_upload_file
from app.utils.logging import logger


import uuid

router = APIRouter()

@router.post('/upload-item')
async def upload_marketplace_item(
    name: str = Form(...),
    category: str = Form(...),
    price: int = Form(...),
    store: str = Form(...),
    file: UploadFile = File(...),
    vector_db: VectorDatabase = Depends(get_marketplace_db)
):
    try:
        logger.info("Received marketplace item image")
        # Generate a unique ID
        item_id = str(uuid.uuid4())
        
        # Save the file first
        image_path = await save_upload_file(file, item_id, 'marketplace')
        
        # Process directly
        with open(image_path, "rb") as f:
            point_id = vector_db.upload_marketplace_clothing(f, name, category, item_id, price, store)
        
        return {
            "id": item_id,
            "status": "completed",
            "name": name,
            "category": category,
            "price": price,
            "store": store,
            "image_path": image_path,
            "vector_id": point_id,
            "message": "Marketplace item uploaded successfully."
        }
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error in upload_marketplace_item: {str(e)}\n{error_details}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.get('/marketplace')
async def get_marketplace(
    vector_db: VectorDatabase = Depends(get_marketplace_db),
):
    try:
        marketplace_items = vector_db.retrieve_collection()
        return {
            "items": marketplace_items
        }
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error in upload_clothing: {str(e)}\n {error_details}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
    
@router.get('/get-item/{item_id}', response_model=MarketplaceItem)
async def get_item(
    item_id: str,
    vector_db: VectorDatabase = Depends(get_marketplace_db)
):
    try:
        item = vector_db.get_items_by_id(item_id)
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item with ID {item_id} not found"
            )
            
        # Format the response according to MarketplaceItem schema
        marketplace_item = MarketplaceItem(
            id=item.id,
            name=item.payload.get("name", "Unnamed Item"),
            category=item.payload.get("category", "uncategorized"),
            tags=item.payload.get("tags", []),
            store=item.payload.get("store", "Unknown Store"),
            price=item.payload.get("price", 0)
        )
        
        return marketplace_item
        
    except HTTPException:
        raise
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error in get_item: {str(e)}\n {error_details}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

