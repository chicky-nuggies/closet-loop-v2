from pydantic import BaseModel
from typing import List, Literal, Union, Any, Optional

class ClothingItem(BaseModel):
    id: Union[str, Any]
    name: str
    tags: List[str]
    category: Literal['top', 'bottom']

class MarketplaceItem(ClothingItem):
    store: str
    price: int

class Outfit(BaseModel):
    score: float
    top: ClothingItem
    bottom: ClothingItem
    prompt: Union[str, None]

class OutfitRequest(BaseModel):
    query: str
    limit: Optional[int] = 3

class OutfitResponse(BaseModel):
    outfits: List[Outfit]
