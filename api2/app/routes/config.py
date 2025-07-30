from fastapi import APIRouter

router = APIRouter()

@router.get("/config")
async def get_config():
    """Get application configuration"""
    return {
        "appTitle": "Ticket Orchestration Chat",
        "appDescription": "BestEgg Support Ticket Orchestration Chat",
        "version": "1.0.0",
        "emailLoginEnabled": True,
        "registrationEnabled": True,
        "socialLoginEnabled": False,
        "passwordResetEnabled": True,
        # Add any other flags your frontend expects
        "features": {
            "registration": True,
            "socialLogin": False,
            "fileUpload": True,
            "multiUser": True
        },
        "endpoints": {
            "openAI": True,
            "anthropic": True,
            "google": False,
            "azure": False
        }
    } 