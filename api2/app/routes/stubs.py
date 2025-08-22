'''
Placeholders for the actual implementation of the routes.
'''

from fastapi import APIRouter
from app.utils.response_utils import ApiResponse

router = APIRouter()

# PRESETS
@router.get("/presets")
async def get_presets():
    """Get chat presets - stub implementation"""
    return ApiResponse.create_success(
        data=[],
        message="Presets retrieved successfully"
    )

# KEYS
@router.get("/keys")
async def get_keys(name: str = None):
    """Get API keys - stub implementation"""
    return ApiResponse.create_success(
        data={
            "keys": [],
            "total": 0
        },
        message="Keys retrieved successfully"
    )

# AGENTS
@router.get("/agents/tools/web_search/auth")
async def get_web_search_auth():
    """Get web search tool authentication - stub implementation"""
    return ApiResponse.create_success(
        data={
            "enabled": False,
            "authenticated": False
        },
        message="Web search auth status retrieved"
    )

@router.get("/agents/tools/execute_code/auth")
async def get_execute_code_auth():
    """Get code execution tool authentication - stub implementation"""
    return ApiResponse.create_success(
        data={
            "enabled": False,
            "authenticated": False
        },
        message="Code execution auth status retrieved"
    )

# ROLES 
@router.get("/roles/user")
async def get_user_roles():
    """Get user roles - stub implementation"""
    return ApiResponse.create_success(
        data={
            "roles": ["user"],
            "defaultRole": "user"
        },
        message="User roles retrieved successfully"
    )

# SEARCH
@router.get("/search/enable")
async def get_search_enable():
    """Get search functionality status - stub implementation"""
    return ApiResponse.create_success(
        data={
            "enabled": False,
            "provider": "none"
        },
        message="Search status retrieved"
    )

# BANNER
@router.get("/banner")
async def get_banner():
    """Get application banner information"""
    return ApiResponse.create_success(
        data={
            "enabled": False,
            "message": "",
            "type": "info"
        },
        message="Banner information retrieved"
    )

# SHARE
@router.get("/share/link/{link_id}")
async def get_shared_link(link_id: str):
    """Get shared conversation link - stub implementation"""
    return ApiResponse.create_success(
        data={
            "id": link_id,
            "conversationId": None,
            "shareId": link_id,
            "title": "Shared Conversation",
            "createdAt": None,
            "updatedAt": None,
            "isPublic": False
        },
        message="Shared link retrieved successfully"
    )

# AGENT TOOL CALLS history
@router.get("/agents/tools/calls")
async def get_agent_tool_calls(conversationId: str = None):
    """Get agent tool calls for a conversation - stub implementation"""
    return ApiResponse.create_success(
        data={
            "calls": [],
            "total": 0
        },
        message="Agent tool calls retrieved successfully"
    ) 