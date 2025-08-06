from fastapi import APIRouter
from app.utils.response_utils import ApiResponse

router = APIRouter()

@router.get("/files")
async def get_files():
    """Get user files - stub implementation"""
    return ApiResponse.create_success(
        data=[],
        message="Files retrieved successfully"
    )

@router.get("/files/speech/config/get")
async def get_speech_config():
    """Get speech configuration - stub implementation"""
    return ApiResponse.create_success(
        data={
            "enabled": False,
            "provider": "none"
        },
        message="Speech config retrieved successfully"
    )

@router.get("/files/config")
async def get_files_config():
    """Get file upload configuration - stub implementation"""
    return ApiResponse.create_success(
        data={
            "enabled": True,
            "maxSize": 10485760,  # 10MB
            "allowedTypes": ["image/*", "text/*", "application/pdf"]
        },
        message="Files config retrieved successfully"
    ) 