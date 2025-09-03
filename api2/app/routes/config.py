from fastapi import APIRouter
from app.utils.response_utils import ApiResponse
from app.constants import ACTIVE_MODEL
from app.config import settings

router = APIRouter()

@router.get("/config")
async def get_config():
    """Get application configuration"""
    config_data = {
        "appTitle": "Ticket Orchestration Chat",
        "appDescription": "BestEgg Support Ticket Orchestration Chat",
        "version": "1.0.0",
        "emailLoginEnabled": True,
        "registrationEnabled": True,
        "socialLoginEnabled": False,
        "passwordResetEnabled": True,
        "activeModel": ACTIVE_MODEL,
        "activeProvider": settings.llm_provider,
        # Add any other flags your frontend expects
        "features": {
            "registration": True,
            "socialLogin": False,
            "fileUpload": True,
            "multiUser": True
        },
        "endpoints": {
            "custom": True,
            "openAI": False,
            "anthropic": False,
            "google": False,
            "azure": False
        }
    }
    return ApiResponse.create_success(
        data=config_data,
        message="Configuration retrieved successfully"
    )

@router.get("/startup")
async def get_startup_config():
    """Get startup configuration for the frontend"""
    startup_config = {
        "appTitle": "Ticket Orchestration Chat",
        "appDescription": "BestEgg Support Ticket Orchestration Chat",
        "version": "1.0.0",
        "emailLoginEnabled": True,
        "registrationEnabled": True,
        "socialLoginEnabled": False,
        "passwordResetEnabled": True,
        "activeModel": ACTIVE_MODEL,
        "activeProvider": settings.llm_provider,
        "features": {
            "registration": True,
            "socialLogin": False,
            "fileUpload": True,
            "multiUser": True
        },
        "endpoints": {
            "custom": True,
            "openAI": False,
            "anthropic": False,
            "google": False,
            "azure": False
        }
    }
    return ApiResponse.create_success(
        data=startup_config,
        message="Startup configuration retrieved successfully"
    ) 