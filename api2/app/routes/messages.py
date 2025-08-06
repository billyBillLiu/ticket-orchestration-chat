from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import get_db
from app.models.user import User
from app.schemas.message import MessageResponse, MessageCreate, MessageUpdate, MessageListResponse
from app.routes.auth import get_current_user
from app.services.message_service import MessageService

router = APIRouter(tags=["Messages"])

@router.get("/{conversation_id}/messages", response_model=MessageListResponse)
async def get_conversation_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100)
):
    """
    Get all messages for a specific conversation.
    Supports pagination and ensures user can only access their own conversations.
    """
    try:
        message_service = MessageService(db)
        messages, total = message_service.get_conversation_messages(
            conversation_id, current_user.id, page, limit
        )
        
        # Convert to response models
        message_responses = [MessageResponse.model_validate(msg) for msg in messages]
        
        return MessageListResponse(
            messages=message_responses,
            total=total
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching messages: {str(e)}"
        )

@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def create_message(
    conversation_id: int,
    message: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new message in a conversation.
    """
    try:
        message_service = MessageService(db)
        new_message = message_service.create_message(
            conversation_id, current_user.id, message
        )
        
        return MessageResponse.model_validate(new_message)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating message: {str(e)}"
        )

@router.get("/messages/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific message by ID.
    """
    try:
        message_service = MessageService(db)
        message = message_service.get_message(message_id, current_user.id)
        
        return MessageResponse.model_validate(message)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching message: {str(e)}"
        )

@router.put("/messages/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: str,
    message_update: MessageUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a specific message.
    """
    try:
        message_service = MessageService(db)
        updated_message = message_service.update_message(
            message_id, current_user.id, message_update
        )
        
        return MessageResponse.model_validate(updated_message)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating message: {str(e)}"
        )

@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific message.
    """
    try:
        message_service = MessageService(db)
        message_service.delete_message(message_id, current_user.id)
        
        return {"message": "Message deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting message: {str(e)}"
        ) 