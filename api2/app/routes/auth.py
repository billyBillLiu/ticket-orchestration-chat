from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional, Union
from pydantic import BaseModel

from app.models import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserLoginResponse, UserResponse
from app.utils.response_utils import ApiResponse, create_success_response, create_error_response
from app.config import settings
from app.utils.email import send_verification_email
from app.utils.auth_utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    generate_verification_token,
    decode_token,
    create_refresh_token,
    verify_refresh_token
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == user_data.email) |
            ((User.username == user_data.username) if user_data.username else False)
        ).first()
        
        if existing_user:
            return ApiResponse.create_error(
                message="User with this email or username already exists",
                error_type="USER_EXISTS"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username if user_data.username else None,
            email=user_data.email,
            password=hashed_password,
            name=user_data.name if user_data.name else None,
            avatar=user_data.avatar,
            role=user_data.role,
            provider=user_data.provider,
            email_verified=True  # Change to false if adding back verification system
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # commented out since not sending verification email
        # token = generate_verification_token(getattr(db_user, 'id'), getattr(db_user, 'email'))
        # send_verification_email(getattr(db_user, 'email'), token)
        
        # Convert SQLAlchemy model to Pydantic model for serialization
        user_response = UserResponse.model_validate(db_user)
        
        return ApiResponse.create_success(
            data={"user": user_response},
            message="User registered successfully"
        )
        
    except Exception as e:
        # Rollback the transaction in case of error
        db.rollback()
        return ApiResponse.create_error(
            message=f"Registration failed: {str(e)}",
            error_type="REGISTRATION_ERROR"
        )

@router.post("/login")
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, getattr(user, "password")):
        return ApiResponse.create_error(
            message="Incorrect email or password",
            error_type="AUTHENTICATION_FAILED",
            error_code=401,
        )

    # commented out since not checking for email_verified
    # if not user.email_verified:
    #     raise HTTPException(status_code=403, detail="Email not verified")

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    user_response = UserResponse.model_validate(user)
    
    # Return old response structure for backward compatibility
    return ApiResponse.create_success(
        data={
            "token": access_token,
            "token_type": "bearer",
            "user": user_response,
        },
        message="Login successful"
    )

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    user_response = UserResponse.model_validate(current_user)
    return ApiResponse.create_success(
        data={"user": user_response},
        message="User information retrieved successfully"
    )

@router.post("/logout")
async def logout():
    # In a stateless JWT setup, logout is handled client-side
    # You might want to implement a token blacklist for additional security
    return {"message": "Logout successful"}

@router.post("/refresh")
async def refresh_token(token: Optional[str] = Depends(oauth2_scheme)):
    """Refresh the access token"""
    if not token:
        # No token provided, return a response indicating this
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Decode the token to get user info
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except HTTPException:
        # Token is expired or invalid
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    db = next(get_db())
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    user_response = UserResponse.model_validate(user)
    
    # Return old response structure for backward compatibility
    return {
        "token": access_token,
        "token_type": "bearer",
        "user": user_response.model_dump()
    }

@router.post("/verify")
async def verify_email(email: str = Body(...), token: str = Body(...), db: Session = Depends(get_db)):
    # Always return success, do not update any user fields
    return ApiResponse.create_success(
        message="Email verification is disabled"
    ) 