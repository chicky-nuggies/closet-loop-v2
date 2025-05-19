from pydantic import BaseModel
from typing import List, Literal

class ClothingItem(BaseModel):
    name: str
    tags: List[str]
    category: Literal['top', 'bottom']