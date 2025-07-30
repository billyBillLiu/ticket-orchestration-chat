from fastapi import APIRouter

router = APIRouter()

@router.get("/presets")
async def get_presets():
    """Get chat presets - stub implementation"""
    return [] 