from fastapi import APIRouter

router = APIRouter()

@router.get("/files")
async def get_files():
    """Get user files - stub implementation"""
    return []

@router.get("/files/speech/config/get")
async def get_speech_config():
    """Get speech configuration - stub implementation"""
    return {
        "enabled": False,
        "provider": "none"
    }

@router.get("/files/config")
async def get_files_config():
    """Get file upload configuration - stub implementation"""
    return {
        "enabled": True,
        "maxSize": 10485760,  # 10MB
        "allowedTypes": ["image/*", "text/*", "application/pdf"]
    } 