from fastapi import APIRouter

router = APIRouter()

@router.get("/models")
async def get_models():
    # Return models in the format the frontend expects
    models_data = {
        "openAI": [
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4o",
        ]
    }
    return models_data 