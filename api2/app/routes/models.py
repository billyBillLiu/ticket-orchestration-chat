from fastapi import APIRouter

router = APIRouter()

@router.get("/models")
async def get_models():
    # Return models in the format the frontend expects
    models_data = {
        "custom": [
            "deepseek-r1:8b",
            "llama2:7b",
            "mistral:7b",
        ]
    }
    return models_data 