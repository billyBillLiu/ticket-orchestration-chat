from fastapi import APIRouter

router = APIRouter()

@router.get("/banner")
async def get_banner():
    """Get application banner information"""
    return {
        "enabled": False,
        "message": "",
        "type": "info"
    } 