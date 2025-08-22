from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.models import get_db
from app.models.user import User
from app.schemas.conversation import ConversationResponse
from app.routes.auth import get_current_user
from app.services.conversation_service import ConversationService
from app.utils.response_utils import ApiResponse
from app.constants import ACTIVE_MODEL, ACTIVE_PROVIDER

# Request model for the update endpoint
class UpdateConversationRequest(BaseModel):
    arg: dict  # The frontend sends { arg: payload }

# Request model for delete conversations
class DeleteConversationRequest(BaseModel):
    arg: dict  # The frontend sends { arg: payload }

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
        
        # Convert to response models and add model/endpoint info
        conversation_responses = []
        for conv in conversations:
            response = ConversationResponse.model_validate(conv)
            # Set model and endpoint from conversation or use defaults
            response.model = conv.model or ACTIVE_MODEL
            response.endpoint = conv.endpoint or ACTIVE_PROVIDER
            conversation_responses.append(response)
        
        # Debug: Log the response data
        response_data = {
            "conversations": [conv.model_dump() for conv in conversation_responses],
            "nextCursor": None  # For now, no pagination cursor
        }
        
        return ApiResponse.create_success(
            data=response_data,
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
        
        # Create response with model/endpoint info
        response = ConversationResponse.model_validate(conversation)
        response.model = conversation.model or ACTIVE_MODEL
        response.endpoint = conversation.endpoint or ACTIVE_PROVIDER
        
        return ApiResponse.create_success(
            data=response.model_dump(),
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
        
        # Create response with model/endpoint info
        response = ConversationResponse.model_validate(conversation)
        response.model = conversation.model or ACTIVE_MODEL
        response.endpoint = conversation.endpoint or ACTIVE_PROVIDER
        
        return ApiResponse.create_success(
            data=response.model_dump(),
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

@router.post("/update")
async def update_conversation_post(
    request: UpdateConversationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a conversation (POST endpoint for frontend compatibility).
    This endpoint matches the format expected by the frontend.
    """
    try:
        # Extract the actual payload from the arg wrapper
        update_data = request.arg
        
        if not update_data.get('conversationId'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="conversationId is required"
            )
        
        # Convert string conversationId to int for the service
        try:
            conversation_id = int(update_data['conversationId'])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid conversation ID format"
            )
        
        conversation_service = ConversationService(db)
        conversation = conversation_service.update_conversation(
            conversation_id, 
            current_user.id, 
            update_data.get('title'), 
            update_data.get('is_archived')
        )
        
        # Return the conversation object directly to match the original API format
        return ConversationResponse.model_validate(conversation).model_dump()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating conversation: {str(e)}"
        )

# Note: This endpoint is moved after the general DELETE "/" endpoint to avoid conflicts

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

@router.post("/gen_title")
async def generate_title(
    conversationId: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a title for a conversation.
    Note: This is a stub implementation - you may want to implement actual title generation.
    """
    try:
        # For now, return a placeholder title
        # In a real implementation, you would generate a title based on conversation content
        title = f"Conversation {conversationId}"
        
        return ApiResponse.create_success(
            data={"title": title},
            message="Title generated successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating title: {str(e)}"
        )

@router.delete("")
@router.delete("/")
async def delete_conversations(
    conversationId: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    thread_id: Optional[str] = Query(None),
    endpoint: Optional[str] = Query(None),
    request_body: Optional[DeleteConversationRequest] = Body(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete conversations based on filter criteria.
    Supports:
    - Single conversation deletion by ID
    - Bulk deletion by thread_id or endpoint
    - Request body payload (for frontend compatibility)
    """
    try:
        # Extract parameters from request body if provided
        if request_body and request_body.arg:
            payload = request_body.arg
            conversationId = payload.get('conversationId') or conversationId
            source = payload.get('source') or source
            thread_id = payload.get('thread_id') or thread_id
            endpoint = payload.get('endpoint') or endpoint
        
        # Prevent deletion of all conversations without parameters
        if not conversationId and not source and not thread_id and not endpoint:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No parameters provided. Please specify conversationId, thread_id, or endpoint."
            )
        
        conversation_service = ConversationService(db)
        deleted_count = 0
        
        if conversationId:
            # Delete specific conversation
            try:
                conv_id = int(conversationId)
                conversation_service.delete_conversation(conv_id, current_user.id)
                deleted_count = 1
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid conversation ID format"
                )
        elif thread_id:
            # Delete conversations by thread_id
            deleted_count = conversation_service.delete_conversations_by_thread_id(thread_id, current_user.id)
        elif endpoint:
            # Delete conversations by endpoint
            deleted_count = conversation_service.delete_conversations_by_endpoint(endpoint, current_user.id)
        elif source == 'button':
            return ApiResponse.create_success(
                data={"message": "No conversationId provided"},
                message="No conversation to delete"
            )
        
        if deleted_count == 0:
            return ApiResponse.create_success(
                data={"message": "No conversations found to delete"},
                message="No conversations found to delete"
            )
        
        return ApiResponse.create_success(
            data={
                "message": f"Successfully deleted {deleted_count} conversation(s)",
                "deleted_count": deleted_count
            },
            message=f"Successfully deleted {deleted_count} conversation(s)"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting conversations: {str(e)}"
        )

# Specific conversation delete endpoint (moved to avoid conflicts)
@router.delete("/id/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a conversation by ID in the URL path.
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

@router.delete("/all")
async def delete_all_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete all conversations for the current user.
    """
    try:
        conversation_service = ConversationService(db)
        deleted_count = conversation_service.delete_all_user_conversations(current_user.id)
        
        return ApiResponse.create_success(
            data={
                "message": f"All conversations deleted successfully",
                "deleted_count": deleted_count
            },
            message=f"Successfully deleted {deleted_count} conversations"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting all conversations: {str(e)}"
        )



 