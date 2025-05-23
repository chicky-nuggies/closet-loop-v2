import numpy as np

from app.services.vector_db import VectorDatabase
from app.utils.embeddings import embed_text
from app.models.schemas import ClothingItem, Outfit

def generate_outfit(query: str, vector_db: VectorDatabase, limit: int = 3):
    query_embedding = embed_text(query, vector_db.processor, vector_db.model)
    
    # Get top candidates
    tops = vector_db.get_items_by_category("top", query_embedding, limit)
    # Get bottom candidates
    bottoms = vector_db.get_items_by_category("bottom", query_embedding, limit)
    
    if not tops or not bottoms:
        return []
    
    # Score and get outfit pairs
    return _score_outfit_combinations(query_embedding, tops, bottoms, query, limit)

def _score_outfit_combinations(query_embedding, tops, bottoms, query, limit: int = 3, ):
    """Score outfit combinations based on coherence and query relevance"""
    pair_scores = []
    for top in tops:
        for bottom in bottoms:
            top_vector = np.array(top.vector)
            bottom_vector = np.array(bottom.vector)
            
            coherence = _cosine_similarity(top_vector, bottom_vector)
            query_relevance = (
                _cosine_similarity(query_embedding, top_vector) +
                _cosine_similarity(query_embedding, bottom_vector)
            ) / 2
            
            # Prepare payload with item IDs
            top_payload = top.payload.copy() if hasattr(top, 'payload') else {}
            bottom_payload = bottom.payload.copy() if hasattr(bottom, 'payload') else {}
            top_payload['id'] = top.id
            bottom_payload['id'] = bottom.id
            
            score = 0.5 * query_relevance + 0.5 * coherence
            
            # Create proper ClothingItem objects
            top_item = ClothingItem(
                id=top.id,
                name=top_payload.get('name', f"Item {top.id}"),
                tags=top_payload.get('tags', []),
                category='top'
            )
            
            bottom_item = ClothingItem(
                id=bottom.id,
                name=bottom_payload.get('name', f"Item {bottom.id}"),
                tags=bottom_payload.get('tags', []),
                category='bottom'
            )
            
            # Create Outfit object
            outfit = Outfit(
                score=score,
                top=top_item,
                bottom=bottom_item,
                prompt=query
            )
            
            pair_scores.append(outfit)

    pair_scores.sort(key=lambda x: x.score, reverse=True)
    return pair_scores[:limit]

def _cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors"""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


