import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware 

from app.api.routes import router
from app.services.vector_db import VectorDatabase
from app.utils.model_loader import load_model
from app.utils.logging import logger
from app.dependencies import app_state



# Load environment variables
load_dotenv()

QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_API_KEY =os.getenv("QDRANT_THRIFT_API_KEY")
QDRANT_WARDROBE_COLLECTION = os.getenv('QDRANT_WARDROBE_COLLECTION')
QDRANT_MARKETPLACE_COLLECTION = os.getenv('QDRANT_MARKETPLACE_COLLECTION')
# CLOTHING_TAGS = os.getenv('CLOTHING_TAGS')

class AppState:
    def __init__(self):
        self.model = None
        self.processor = None
        self.vector_db_marketplace = None
        self.vector_db_wardrobe = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        logger.info("Starting up...")

        # Load model
        app_state.processor, app_state.model = load_model()

        # Initialize Qdrant clients
        app_state.vector_db_marketplace = VectorDatabase(
            host=QDRANT_HOST, 
            api_key=QDRANT_API_KEY, 
            collection_name=QDRANT_MARKETPLACE_COLLECTION,
            model=app_state.model,
            processor=app_state.processor
        )
        app_state.vector_db_wardrobe = VectorDatabase(
            host=QDRANT_HOST, 
            api_key=QDRANT_API_KEY, 
            collection_name=QDRANT_WARDROBE_COLLECTION,
            model=app_state.model,
            processor=app_state.processor
        )
        
        logger.info("Startup completed successfully!")

    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise

    yield 

    # Shutdown
    try:
        logger.info("Shutting down...")
        # Cleanup resources if needed
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


app = FastAPI(title="My FastAPI App", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

app.mount("/static", StaticFiles(directory='app/static'))

app.include_router(router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI app!"}
