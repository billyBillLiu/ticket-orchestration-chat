from fastapi import APIRouter

router = APIRouter()

@router.get("/roles/user")
async def get_user_roles():
    """Get user roles - stub implementation"""
    return {
        "roles": ["user"],
        "defaultRole": "user"
    } 