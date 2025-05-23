from fastapi import HTTPException

# App state to be initialized in main.py
class AppState:
    def __init__(self):
        self.model = None
        self.processor = None
        self.vector_db_marketplace = None
        self.vector_db_wardrobe = None

# Global app state
app_state = AppState()

# Dependencies
def get_model():
    if app_state.model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    return app_state.model

def get_processor():
    if app_state.processor is None:
        raise HTTPException(status_code=500, detail="Processor not loaded")
    return app_state.processor

def get_marketplace_db():
    if app_state.vector_db_marketplace is None:
        raise HTTPException(status_code=500, detail="Marketplace DB not initialized")
    return app_state.vector_db_marketplace

def get_wardrobe_db():
    if app_state.vector_db_wardrobe is None:
        raise HTTPException(status_code=500, detail="Wardrobe DB not initialized")
    return app_state.vector_db_wardrobe