from fastapi import APIRouter, Depends, HTTPException, status, Request, Body, Form
from sqlalchemy.orm import Session
from app.models import get_db
from app.models.user import User
from app.routes.auth import get_current_user, generate_verification_token
from app.utils.email import send_verification_email

router = APIRouter()

@router.get("/user")
async def get_user(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "name": current_user.name,
        "avatar": current_user.avatar,
        "role": current_user.role,
        "provider": current_user.provider
    }