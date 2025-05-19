from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="My FastAPI App")

app.include_router(router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI app!"}
