# ClosetLoop Backend

This is the backend service for ClosetLoop, a smart wardrobe and outfit recommendation application. It uses FastAPI to provide a RESTful API for managing clothing items, generating outfit suggestions, and interacting with a marketplace.

## Overview

The backend leverages a pre-trained CLIP model for generating image and text embeddings, and Qdrant as a vector database for efficient similarity search. This allows for features like:

- Uploading and managing personal wardrobe items.
- Generating outfit recommendations based on text queries (e.g., "casual outfit for a sunny day").
- Listing and searching for items in a marketplace.

## Features

- **Wardrobe Management**: Upload, view, and delete clothing items from your personal wardrobe.
- **Outfit Generation**: Get outfit suggestions (top and bottom combinations) based on descriptive text queries.
- **Marketplace**: Upload and view items available in a marketplace, including price and store information.
- **Image-based Search**: Clothing items are indexed by their visual features, enabling semantic search.
- **Tagging**: Automatic tagging of clothing items based on visual similarity.

## Setup

### Prerequisites

- Python 3.9+
- Poetry (or pip) for dependency management
- Access to a Qdrant instance

### Installation

1.  **Clone the repository:**

    ```bash
    git clone <your-repository-url>
    cd closetloop-backend
    ```

2.  **Install dependencies:**
    Using Poetry:

    ```bash
    poetry install
    ```

    Or using pip:

    ```bash
    pip install -r requirements.txt
    ```

    _(You'll need to generate a `requirements.txt` file if you don't have one: `poetry export -f requirements.txt --output requirements.txt --without-hashes`)_

3.  **Set up the CLIP model:**
    The model files are expected in the `app/model/` directory. Ensure you have the `config.json`, `merges.txt`, `model.safetensors`, `preprocessor_config.json`, etc., files in this location. This directory is currently ignored by git (as per your [`.gitignore`](.gitignore) file), so you'll need to acquire and place these files manually.

### Environment Variables

Create a `.env` file in the root directory of the project and add the following environment variables. See [app/main.py](app/main.py) for how these are used.

```env
# .env
QDRANT_HOST="your_qdrant_host_url"
QDRANT_API_KEY="your_qdrant_api_key"
QDRANT_WARDROBE_COLLECTION="wardrobe" # Or your preferred collection name
QDRANT_MARKETPLACE_COLLECTION="marketplace" # Or your preferred collection name
# CLOTHING_TAGS (Optional, if you have a predefined list for some functionality)
```

Ensure your Qdrant instance has collections named `wardrobe`, `marketplace`, and `tags` (as used in [`app.services.vector_db.VectorDatabase._get_tags`](app/services/vector_db.py)). The `tags` collection is used by the `_get_tags` method in the [`VectorDatabase`](app/services/vector_db.py) class.

## Running the Application

To run the FastAPI application, use Uvicorn:

```bash
uvicorn app.main:app --reload
```

The application will typically be available at `http://127.0.0.1:8000`.

## API Endpoints

The API is structured with the following main groups, prefixed with `/api`:

- **`/api/wardrobe/`**: Endpoints for managing wardrobe items.
  - `POST /upload-clothing`: Upload a new clothing item.
  - `GET /wardrobe`: Retrieve all items in the wardrobe.
  - `DELETE /delete-clothing/{clothing_id}`: Delete a specific clothing item.
  - `GET /upload-status/{task_id}`: Check the status of an upload task (if using background tasks, though current implementation is direct).
- **`/api/outfit/`**: Endpoints for outfit generation.
  - `POST /generate-outfit`: Generate outfit recommendations based on a query.
- **`/api/marketplace/`**: Endpoints for marketplace items.
  - `POST /upload-item`: Upload a new item to the marketplace.
  - `GET /marketplace`: Retrieve all items in the marketplace.
  - `GET /get-item/{item_id}`: Retrieve a specific marketplace item.

For detailed request and response schemas, refer to the OpenAPI documentation available at `http://127.0.0.1:8000/docs` when the application is running.

The main router is defined in [app/api/routes.py](app/api/routes.py).
