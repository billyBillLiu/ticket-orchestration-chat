from fastapi import APIRouter

router = APIRouter()

@router.get("/search/enable")
async def get_search_enable():
    """Get search functionality status - stub implementation"""
    return {
        "enabled": False,
        "provider": "none"
    } 