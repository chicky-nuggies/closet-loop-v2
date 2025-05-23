from PIL import Image
import torch
import numpy as np
from io import BytesIO

def embed_image(image_data: bytes, processor, model):
    
    image = Image.open(BytesIO(image_data))
    inputs = processor(images=image, return_tensors="pt")
    
    with torch.no_grad():
        outputs = model.get_image_features(**inputs)
    
    embeddings = outputs.numpy()
    embeddings = embeddings / np.linalg.norm(embeddings)
    
    return embeddings[0]

def embed_text(text, processor, model):
    inputs = processor(text=text, return_tensors="pt", padding=True)
    
    with torch.no_grad():
        outputs = model.get_text_features(**inputs)
    
    embeddings = outputs.numpy()
    embeddings = embeddings / np.linalg.norm(embeddings)
    
    return embeddings[0]