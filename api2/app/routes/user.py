from fastapi import APIRouter, Depends, HTTPException, status, Request, Body, Form
from sqlalchemy.orm import Session
from app.models import get_db
from app.models.user import User
from app.routes.auth import get_current_user, generate_verification_token
from app.utils.email import send_verification_email

router = APIRouter()

from app.schemas.user import UserResponse
from app.utils.response_utils import ApiResponse

@router.get("/user")
async def get_user(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    user_response = UserResponse.model_validate(current_user)
    
    # Return old response structure for backward compatibility
    return user_response.model_dump()