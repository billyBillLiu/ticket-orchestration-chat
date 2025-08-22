from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from datetime import datetime

from app.models.conversation import Conversation
from app.models.user import User
from app.services.base_service import BaseService
from app.schemas.conversation import ConversationResponse
from app.constants import ACTIVE_MODEL, ACTIVE_PROVIDER

class ConversationService(BaseService):
    """
    Service for managing conversations.
    Handles CRUD operations for conversations with proper authorization.
    """
    
    def get_user_conversations(
        self, 
        user_id: int,
        page: int = 1,
        limit: int = 20,
        archived: Optional[bool] = None
    ) -> Tuple[List[Conversation], int]:
        """
        Get conversations for a user with pagination and filtering.
        
        Args:
            user_id: ID of the user
            page: Page number (1-based)
            limit: Number of conversations per page
            archived: Filter by archived status (None for all)
            
        Returns:
            Tuple of (conversations_list, total_count)
        """
        # Build query
        query = self.db.query(Conversation).filter(Conversation.user_id == user_id)
        
        # Filter by archived status if specified
        if archived is not None:
            query = query.filter(Conversation.is_archived == archived)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        conversations = query.order_by(Conversation.updated_at.desc()).offset(offset).limit(limit).all()
        
        return conversations, total
    
    def create_conversation(self, user_id: int, title: Optional[str] = None) -> Conversation:
        """
        Create a new conversation for a user.
        
        Args:
            user_id: ID of the user
            title: Optional title for the conversation
            
        Returns:
            Created conversation
        """
        
        new_conversation = Conversation(
            user_id=user_id,
            title=title or "New Conversation",
            model=ACTIVE_MODEL,
            endpoint=ACTIVE_PROVIDER
        )
        
        self.db.add(new_conversation)
        self.db.commit()
        self.db.refresh(new_conversation)
        
        # Update title with conversation ID if no custom title was provided
        if not title:
            new_conversation.title = f"Conversation {new_conversation.id}"
            self.db.commit()
            self.db.refresh(new_conversation)
        
        return new_conversation
    
    def get_conversation(self, conversation_id: int, user_id: int) -> Conversation:
        """
        Get a specific conversation by ID, ensuring user owns it.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for security)
            
        Returns:
            Conversation object
        """
        return self.verify_user_owns_conversation(user_id, conversation_id)
    
    def update_conversation(
        self, 
        conversation_id: int, 
        user_id: int,
        title: Optional[str] = None,
        is_archived: Optional[bool] = None
    ) -> Conversation:
        """
        Update a conversation.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for security)
            title: New title (optional)
            is_archived: Archive status (optional)
            
        Returns:
            Updated conversation
        """
        conversation = self.verify_user_owns_conversation(user_id, conversation_id)
        
        # Update fields
        if title is not None:
            conversation.title = title
        if is_archived is not None:
            conversation.is_archived = is_archived
        
        conversation.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(conversation)
        
        return conversation
    
    def delete_conversation(self, conversation_id: int, user_id: int) -> bool:
        """
        Delete a conversation and all its messages.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for security)
            
        Returns:
            True if deleted successfully
        """
        conversation = self.verify_user_owns_conversation(user_id, conversation_id)
        
        # Delete associated messages first
        from app.models.message import Message
        self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).delete()
        
        # Delete conversation
        self.db.delete(conversation)
        self.db.commit()
        
        return True
    
    def delete_all_user_conversations(self, user_id: int) -> int:
        """
        Delete all conversations for a user and their associated messages.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Number of conversations deleted
        """
        from app.models.message import Message
        
        # Get all conversation IDs for the user
        conversation_ids = self.db.query(Conversation.id).filter(
            Conversation.user_id == user_id
        ).all()
        
        conversation_ids = [conv_id[0] for conv_id in conversation_ids]
        
        if not conversation_ids:
            return 0
        
        # Delete all messages for these conversations
        self.db.query(Message).filter(
            Message.conversation_id.in_(conversation_ids)
        ).delete(synchronize_session=False)
        
        # Delete all conversations
        deleted_count = self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).delete(synchronize_session=False)
        
        self.db.commit()
        
        return deleted_count
    
    def delete_conversations_by_thread_id(self, thread_id: str, user_id: int) -> int:
        """
        Delete all conversations for a user that have a specific thread_id.
        
        Args:
            thread_id: The thread_id to match
            user_id: ID of the user (for security)
            
        Returns:
            Number of conversations deleted
        """
        from app.models.message import Message
        
        # Find conversations that have messages with the specified thread_id
        conversation_ids = self.db.query(Message.conversation_id).filter(
            Message.thread_id == thread_id
        ).distinct().all()
        
        conversation_ids = [conv_id[0] for conv_id in conversation_ids]
        
        if not conversation_ids:
            return 0
        
        # Verify user owns these conversations
        user_conversation_ids = self.db.query(Conversation.id).filter(
            Conversation.id.in_(conversation_ids),
            Conversation.user_id == user_id
        ).all()
        
        user_conversation_ids = [conv_id[0] for conv_id in user_conversation_ids]
        
        if not user_conversation_ids:
            return 0
        
        # Delete all messages for these conversations
        self.db.query(Message).filter(
            Message.conversation_id.in_(user_conversation_ids)
        ).delete(synchronize_session=False)
        
        # Delete conversations
        deleted_count = self.db.query(Conversation).filter(
            Conversation.id.in_(user_conversation_ids)
        ).delete(synchronize_session=False)
        
        self.db.commit()
        
        return deleted_count
    
    def delete_conversations_by_endpoint(self, endpoint: str, user_id: int) -> int:
        """
        Delete all conversations for a user that have messages with a specific endpoint.
        
        Args:
            endpoint: The endpoint to match
            user_id: ID of the user (for security)
            
        Returns:
            Number of conversations deleted
        """
        from app.models.message import Message
        
        # Find conversations that have messages with the specified endpoint
        conversation_ids = self.db.query(Message.conversation_id).filter(
            Message.endpoint == endpoint
        ).distinct().all()
        
        conversation_ids = [conv_id[0] for conv_id in conversation_ids]
        
        if not conversation_ids:
            return 0
        
        # Verify user owns these conversations
        user_conversation_ids = self.db.query(Conversation.id).filter(
            Conversation.id.in_(conversation_ids),
            Conversation.user_id == user_id
        ).all()
        
        user_conversation_ids = [conv_id[0] for conv_id in user_conversation_ids]
        
        if not user_conversation_ids:
            return 0
        
        # Delete all messages for these conversations
        self.db.query(Message).filter(
            Message.conversation_id.in_(user_conversation_ids)
        ).delete(synchronize_session=False)
        
        # Delete conversations
        deleted_count = self.db.query(Conversation).filter(
            Conversation.id.in_(user_conversation_ids)
        ).delete(synchronize_session=False)
        
        self.db.commit()
        
        return deleted_count
    
    def archive_conversation(self, conversation_id: int, user_id: int) -> Conversation:
        """
        Archive a conversation.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for security)
            
        Returns:
            Updated conversation
        """
        return self.update_conversation(conversation_id, user_id, is_archived=True)
    
    def unarchive_conversation(self, conversation_id: int, user_id: int) -> Conversation:
        """
        Unarchive a conversation.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for security)
            
        Returns:
            Updated conversation
        """
        return self.update_conversation(conversation_id, user_id, is_archived=False)
    
    def get_conversation_stats(self, conversation_id: int, user_id: int) -> dict:
        """
        Get statistics for a conversation.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for security)
            
        Returns:
            Dictionary with conversation statistics
        """
        conversation = self.verify_user_owns_conversation(user_id, conversation_id)
        
        from app.models.message import Message
        
        # Get message statistics
        total_messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).count()
        
        user_messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.role == "user"
        ).count()
        
        assistant_messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.role == "assistant"
        ).count()
        
        return {
            "conversation_id": conversation_id,
            "title": conversation.title,
            "total_messages": total_messages,
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "is_archived": conversation.is_archived
        } 