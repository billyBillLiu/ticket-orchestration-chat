from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models import get_db
from app.models.user import User
from app.schemas.conversation import ConversationResponse, ConversationListResponse
from app.routes.auth import get_current_user
from app.services.conversation_service import ConversationService
from app.utils.response_utils import ApiResponse

router = APIRouter(tags=["Conversations"])

@router.get("")
@router.get("/")
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
        conversation_service = ConversationService(db)
        conversations, total = conversation_service.get_user_conversations(
            current_user.id, page, limit, archived
        )
        
        # Convert to response models
        conversation_responses = [ConversationResponse.model_validate(conv) for conv in conversations]
        
        return ApiResponse.create_success(
            data={
                "conversations": [conv.model_dump() for conv in conversation_responses],
                "nextCursor": None  # For now, no pagination cursor
            },
            message="Conversations retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching conversations: {str(e)}"
        )

@router.post("/")
async def create_conversation(
    title: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new conversation for the current user.
    """
    try:
        conversation_service = ConversationService(db)
        conversation = conversation_service.create_conversation(current_user.id, title)
        
        return ApiResponse.create_success(
            data=ConversationResponse.model_validate(conversation).model_dump(),
            message="Conversation created successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating conversation: {str(e)}"
        )

@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific conversation by ID.
    """
    try:
        conversation_service = ConversationService(db)
        conversation = conversation_service.get_conversation(conversation_id, current_user.id)
        
        return ApiResponse.create_success(
            data=ConversationResponse.model_validate(conversation).model_dump(),
            message="Conversation retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching conversation: {str(e)}"
        )

@router.put("/{conversation_id}")
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
    try:
        conversation_service = ConversationService(db)
        conversation = conversation_service.update_conversation(
            conversation_id, current_user.id, title, is_archived
        )
        
        return ApiResponse.create_success(
            data=ConversationResponse.model_validate(conversation).model_dump(),
            message="Conversation updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
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
    try:
        conversation_service = ConversationService(db)
        conversation_service.delete_conversation(conversation_id, current_user.id)
        
        return ApiResponse.create_success(
            data={"message": "Conversation deleted successfully"},
            message="Conversation deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting conversation: {str(e)}"
        )

@router.post("/{conversation_id}/archive")
async def archive_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Archive a conversation.
    """
    try:
        conversation_service = ConversationService(db)
        conversation = conversation_service.archive_conversation(conversation_id, current_user.id)
        
        return ApiResponse.create_success(
            data=ConversationResponse.model_validate(conversation).model_dump(),
            message="Conversation archived successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error archiving conversation: {str(e)}"
        )

@router.post("/{conversation_id}/unarchive")
async def unarchive_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unarchive a conversation.
    """
    try:
        conversation_service = ConversationService(db)
        conversation = conversation_service.unarchive_conversation(conversation_id, current_user.id)
        
        return ApiResponse.create_success(
            data=ConversationResponse.model_validate(conversation).model_dump(),
            message="Conversation unarchived successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error unarchiving conversation: {str(e)}"
        )

@router.get("/{conversation_id}/stats")
async def get_conversation_stats(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics for a conversation.
    """
    try:
        conversation_service = ConversationService(db)
        stats = conversation_service.get_conversation_stats(conversation_id, current_user.id)
        
        return ApiResponse.create_success(
            data=stats,
            message="Conversation stats retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching conversation stats: {str(e)}"
        ) 