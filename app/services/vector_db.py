from qdrant_client import QdrantClient
from fastapi import APIRouter, UploadFile, File, Request
from qdrant_client.models import Filter, FieldCondition, MatchValue, PointStruct

from typing import Literal, Any
import numpy as np  

from app.utils.embeddings import embed_image


class VectorDatabase:
    def __init__(self, host: str, api_key: str, collection_name: str, model: Any, processor: Any):
        self.client = QdrantClient(url=host, api_key=api_key)
        self.collection_name = collection_name
        self.model = model
        self.processor = processor

    def upload_clothing(self, file: UploadFile, name: str, category: Literal['top', 'bottom'], point_id: str) -> int:
        """Upload clothing and returns point id"""
        # Check if we're dealing with a standard file object or an UploadFile
        if hasattr(file, 'file'):
            # It's an UploadFile from FastAPI
            image = file.file.read()
        else:
            # It's a standard file object (like from open())
            image = file.read()
        
        image_embedding = embed_image(image, self.processor, self.model)
        tags = self._get_tags(image_embedding)

        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                {
                    "id": point_id,
                    'vector': image_embedding.tolist(),
                    "payload": {
                    "name": name,
                    "category": category,
                    "tags": tags,
                    }
                },
            ]
        )
        return point_id
    
    def upload_marketplace_clothing(self, file: UploadFile, name: str, category: Literal['top', 'bottom'], point_id: str, price: int, store: str) -> int:
        """Upload clothing and returns point id"""
        # Check if we're dealing with a standard file object or an UploadFile
        if hasattr(file, 'file'):
            # It's an UploadFile from FastAPI
            image = file.file.read()
        else:
            # It's a standard file object (like from open())
            image = file.read()
        
        image_embedding = embed_image(image, self.processor, self.model)
        tags = self._get_tags(image_embedding)

        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                {
                    "id": point_id,
                    'vector': image_embedding.tolist(),
                    "payload": {
                    "name": name,
                    "category": category,
                    "tags": tags,
                    "price": price,
                    "store": store,
                    }
                },
            ]
        )
        return point_id
    
    def retrieve_collection(self) -> list:
        """Returns array of items in the collection"""
        points = self.client.scroll(
            collection_name=self.collection_name,
            limit=100,
        )[0]

        wardrobe_items = []

        for point in points:
            item = {
                "id": point.id,
                "name": point.payload.get("name", "Unnamed Item"),
                "category": point.payload.get("category", "uncategorized"),
                "tags": point.payload.get("tags", [])
            }
            wardrobe_items.append(item)
        
        return wardrobe_items

    def get_items_by_category(self, category: str, query_embedding: np.ndarray, limit: int = 5):
        """Get items by category with similarity search"""
        try:
            return self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding.tolist(),
                query_filter=Filter(
                    must=[FieldCondition(key="category", match=MatchValue(value=category))]
                ),
                with_vectors=True,
                with_payload=True,
                limit=limit
            ).points
        except Exception as e:
            raise Exception(f"Error querying items: {str(e)}")
        
    def get_items_by_id(self, item_id: str):
        """
        Retrieve a specific clothing item from the collection by its ID
        
        Args:
            item_id: The ID of the point/clothing item to retrieve
            
        Returns:
            The clothing item if found, None otherwise
        """
        try:
            result = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[item_id],
                with_payload=True,
                with_vectors=False
            )
            
            if result and len(result) > 0:
                return result[0]
            return None
        except Exception as e:
            print(f"Error retrieving item with ID {item_id}: {str(e)}")
            return None

    def delete_clothing(self, point_id: str) -> bool:
        """
        Delete a clothing item from the collection by its ID
        
        Args:
            point_id: The ID of the point/clothing item to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[point_id]
            )
            return True
        except Exception as e:
            print(f"Error deleting point {point_id}: {str(e)}")
            return False

    def _get_tags(self, image_embedding) -> list:
        result = self.client.query_points(
            collection_name='tags',
            query=image_embedding,
            with_payload=True,
            limit=5
        ).points
        item_tags = [tag.payload['tag'] for tag in result]
        return item_tags



