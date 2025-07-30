from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models import get_db
from app.models.user import User
from app.models.conversation import Conversation
from app.schemas.conversation import ConversationResponse, ConversationListResponse
from app.routes.auth import get_current_user

router = APIRouter(tags=["Conversations"])

@router.get("", response_model=ConversationListResponse)
@router.get("/", response_model=ConversationListResponse)
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    archived: Optional[bool] = Query(None)
):
    """
    Get conversations for the current user.
    Supports pagination and filtering by archived status.
    """
    try:
        # Build query
        query = db.query(Conversation).filter(Conversation.user_id == current_user.id)
        
        # Filter by archived status if specified
        if archived is not None:
            query = query.filter(Conversation.is_archived == archived)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        conversations = query.order_by(Conversation.updated_at.desc()).offset(offset).limit(limit).all()
        
        # Convert to response models
        conversation_responses = [ConversationResponse.model_validate(conv) for conv in conversations]
        
        return ConversationListResponse(
            conversations=conversation_responses,
            total=total
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching conversations: {str(e)}"
        )

@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    title: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new conversation for the current user.
    """
    try:
        conversation = Conversation(
            title=title or f"New conversation {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            user_id=current_user.id
        )
        
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        return ConversationResponse.model_validate(conversation)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating conversation: {str(e)}"
        )

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific conversation by ID.
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return ConversationResponse.model_validate(conversation)

@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    title: Optional[str] = None,
    is_archived: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a conversation.
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    try:
        # Use setattr to avoid type checker issues with SQLAlchemy columns
        if title is not None:
            setattr(conversation, 'title', title)
        if is_archived is not None:
            setattr(conversation, 'is_archived', is_archived)
        
        setattr(conversation, 'updated_at', datetime.utcnow())
        db.commit()
        db.refresh(conversation)
        
        return ConversationResponse.model_validate(conversation)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating conversation: {str(e)}"
        )

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a conversation.
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    try:
        db.delete(conversation)
        db.commit()
        
        return {"message": "Conversation deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting conversation: {str(e)}"
        ) 