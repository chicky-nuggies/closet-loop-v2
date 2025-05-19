from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.models.schemas import ClothingItem

router = APIRouter()

@router.get('/butt', response_model=ClothingItem)
def check():
    return {
        'name': 'grey hoodie',
        'tags': ['balls', 'balls'],
        'category': 'bottom'
    }