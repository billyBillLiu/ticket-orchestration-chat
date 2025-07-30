from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models import get_db
from app.models.user import User
from app.services.memory_service import MemoryService
from app.routes.auth import get_current_user

router = APIRouter(tags=["Memory"])

@router.get("/context/{conversation_id}")
async def get_conversation_context(
    conversation_id: int,
    max_messages: int = Query(20, ge=1, le=100),
    include_system_messages: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get conversation context for AI processing.
    Returns messages in OpenAI-style format for use with AI models.
    """
    try:
        memory_service = MemoryService(db)
        context_messages, conversation_title = memory_service.get_conversation_context(
            conversation_id=conversation_id,
            user_id=current_user.id,
            max_messages=max_messages,
            include_system_messages=include_system_messages
        )
        
        if not context_messages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or no messages available"
            )
        
        return {
            "conversation_id": conversation_id,
            "conversation_title": conversation_title,
            "messages": context_messages,
            "message_count": len(context_messages),
            "max_messages": max_messages
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting conversation context: {str(e)}"
        )

@router.get("/summary/{conversation_id}")
async def get_conversation_summary(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a summary of conversation statistics and metadata.
    """
    try:
        memory_service = MemoryService(db)
        summary = memory_service.get_conversation_summary(
            conversation_id=conversation_id,
            user_id=current_user.id
        )
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting conversation summary: {str(e)}"
        )

@router.get("/user/memory")
async def get_user_memory(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recent conversation memory for the current user.
    Returns summaries of recent conversations.
    """
    try:
        memory_service = MemoryService(db)
        memory = memory_service.get_user_conversation_memory(
            user_id=current_user.id,
            limit=limit
        )
        
        return {
            "user_id": current_user.id,
            "conversations": memory,
            "total_conversations": len(memory),
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user memory: {str(e)}"
        )

@router.get("/search")
async def search_memory(
    query: str = Query(..., min_length=1, max_length=200),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search through conversation memory for specific content.
    """
    try:
        memory_service = MemoryService(db)
        results = memory_service.search_conversation_memory(
            user_id=current_user.id,
            query=query,
            limit=limit
        )
        
        return {
            "query": query,
            "results": results,
            "total_results": len(results),
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching memory: {str(e)}"
        )

@router.get("/timeline/{conversation_id}")
async def get_conversation_timeline(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a timeline of messages in a conversation.
    """
    try:
        memory_service = MemoryService(db)
        timeline = memory_service.get_conversation_timeline(
            conversation_id=conversation_id,
            user_id=current_user.id
        )
        
        if not timeline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or no messages available"
            )
        
        return {
            "conversation_id": conversation_id,
            "timeline": timeline,
            "total_messages": len(timeline)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting conversation timeline: {str(e)}"
        )

@router.post("/cleanup")
async def cleanup_old_conversations(
    days_old: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Archive old conversations to free up memory.
    """
    try:
        memory_service = MemoryService(db)
        archived_count = memory_service.cleanup_old_conversations(
            user_id=current_user.id,
            days_old=days_old
        )
        
        return {
            "message": f"Successfully archived {archived_count} old conversations",
            "archived_count": archived_count,
            "days_old": days_old
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cleaning up conversations: {str(e)}"
        )

@router.get("/stats")
async def get_memory_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get memory statistics for the current user.
    """
    try:
        from app.models.conversation import Conversation
        from app.models.message import Message
        
        # Get conversation stats
        total_conversations = db.query(Conversation).filter(
            Conversation.user_id == current_user.id
        ).count()
        
        active_conversations = db.query(Conversation).filter(
            Conversation.user_id == current_user.id,
            Conversation.is_archived == False
        ).count()
        
        archived_conversations = db.query(Conversation).filter(
            Conversation.user_id == current_user.id,
            Conversation.is_archived == True
        ).count()
        
        # Get message stats
        total_messages = db.query(Message).join(Conversation).filter(
            Conversation.user_id == current_user.id
        ).count()
        
        user_messages = db.query(Message).join(Conversation).filter(
            Conversation.user_id == current_user.id,
            Message.role == "user"
        ).count()
        
        assistant_messages = db.query(Message).join(Conversation).filter(
            Conversation.user_id == current_user.id,
            Message.role == "assistant"
        ).count()
        
        # Get recent activity
        recent_conversations = db.query(Conversation).filter(
            Conversation.user_id == current_user.id
        ).order_by(Conversation.updated_at.desc()).limit(5).all()
        
        recent_activity = []
        for conv in recent_conversations:
            recent_activity.append({
                "conversation_id": conv.id,
                "title": conv.title,
                "updated_at": conv.updated_at.isoformat()
            })
        
        return {
            "user_id": current_user.id,
            "conversations": {
                "total": total_conversations,
                "active": active_conversations,
                "archived": archived_conversations
            },
            "messages": {
                "total": total_messages,
                "user": user_messages,
                "assistant": assistant_messages
            },
            "recent_activity": recent_activity
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting memory stats: {str(e)}"
        ) 