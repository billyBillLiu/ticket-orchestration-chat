from fastapi import APIRouter
from app.constants import ACTIVE_MODEL

router = APIRouter()

@router.get("/models")
async def get_models():
    # Return models in the format the frontend expects
    # Only return the currently active model
    models_data = {
        "custom": [
            ACTIVE_MODEL,  # Use the active model from constants
        ]
    }
    return models_data 