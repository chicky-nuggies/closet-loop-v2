from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional


from app.services.outfit_generation import generate_outfit
from app.services.vector_db import VectorDatabase
from app.dependencies import get_wardrobe_db
from app.models.schemas import OutfitRequest, OutfitResponse

router = APIRouter()


@router.post('/generate-outfit', response_model=OutfitResponse)
def outfit_generate(request: OutfitRequest, vector_db: VectorDatabase = Depends(get_wardrobe_db)):
    """
    Generate outfit recommendations based on a text query.
    
    The query can describe a style, occasion, color preference, etc.
    Returns a list of top outfits, each containing a top and bottom item.
    """
    try:
        outfits = generate_outfit(
            query=request.query, 
            vector_db=vector_db, 
            limit=request.limit
        )
        
        if not outfits:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No suitable outfits found. Try a different query or add more items to your wardrobe."
            )
            
        # return outfits
        return {"outfits": outfits}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate outfits: {str(e)}"
        )