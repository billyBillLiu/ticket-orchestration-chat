from fastapi import APIRouter

router = APIRouter()

@router.get("/keys")
async def get_keys(name: str = None):
    """Get API keys - stub implementation"""
    return {
        "keys": [],
        "total": 0
    } 