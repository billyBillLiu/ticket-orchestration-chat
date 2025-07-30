from fastapi import APIRouter

router = APIRouter()

@router.get("/agents/tools/web_search/auth")
async def get_web_search_auth():
    """Get web search tool authentication - stub implementation"""
    return {
        "enabled": False,
        "authenticated": False
    }

@router.get("/agents/tools/execute_code/auth")
async def get_execute_code_auth():
    """Get code execution tool authentication - stub implementation"""
    return {
        "enabled": False,
        "authenticated": False
    } 