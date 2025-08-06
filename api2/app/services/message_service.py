from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
import uuid
from datetime import datetime

from app.models.conversation import Conversation
from app.models.message import Message
from app.services.base_service import BaseService
from app.schemas.message import MessageCreate, MessageUpdate

class MessageService(BaseService):
    """
    Service for managing messages within conversations.
    Handles CRUD operations for messages with proper authorization.
    """
    
    def get_conversation_messages(
        self, 
        conversation_id: int, 
        user_id: int,
        page: int = 1,
        limit: int = 50
    ) -> Tuple[List[Message], int]:
        """
        Get messages for a conversation with pagination.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for security)
            page: Page number (1-based)
            limit: Number of messages per page
            
        Returns:
            Tuple of (messages_list, total_count)
        """
        # Verify conversation belongs to user using base service method
        conversation = self.verify_user_owns_conversation(user_id, conversation_id)
        
        # Get messages with pagination
        offset = (page - 1) * limit
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).offset(offset).limit(limit).all()
        
        total = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).count()
        
        return messages, total
    
    def create_message(
        self, 
        conversation_id: int, 
        user_id: int,
        message_data: MessageCreate
    ) -> Message:
        """
        Create a new message in a conversation.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for security)
            message_data: Message creation data
            
        Returns:
            Created message
        """
        # Verify conversation belongs to user using base service method
        conversation = self.verify_user_owns_conversation(user_id, conversation_id)
        
        # Create new message
        new_message = Message(
            message_id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            parent_message_id=message_data.parent_message_id,
            role=message_data.role,
            content=message_data.content,
            is_created_by_user=message_data.is_created_by_user
        )
        
        self.db.add(new_message)
        self.db.commit()
        self.db.refresh(new_message)
        
        return new_message
    
    def get_message(self, message_id: str, user_id: int) -> Message:
        """
        Get a specific message by ID, ensuring user owns the conversation.
        
        Args:
            message_id: ID of the message
            user_id: ID of the user (for security)
            
        Returns:
            Message object
        """
        message = self.db.query(Message).filter(Message.message_id == message_id).first()
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
        
        # Verify conversation belongs to user using base service method
        self.verify_user_owns_conversation(user_id, message.conversation_id)
        
        return message
    
    def update_message(
        self, 
        message_id: str, 
        user_id: int,
        message_data: MessageUpdate
    ) -> Message:
        """
        Update a message.
        
        Args:
            message_id: ID of the message
            user_id: ID of the user (for security)
            message_data: Message update data
            
        Returns:
            Updated message
        """
        message = self.get_message(message_id, user_id)
        
        # Update message fields
        if message_data.content is not None:
            message.content = message_data.content
        if message_data.role is not None:
            message.role = message_data.role
        if message_data.is_created_by_user is not None:
            message.is_created_by_user = message_data.is_created_by_user
        
        message.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(message)
        
        return message
    
    def delete_message(self, message_id: str, user_id: int) -> bool:
        """
        Delete a message.
        
        Args:
            message_id: ID of the message
            user_id: ID of the user (for security)
            
        Returns:
            True if deleted successfully
        """
        message = self.get_message(message_id, user_id)
        
        self.db.delete(message)
        self.db.commit()
        
        return True
    
    def get_message_with_conversation(self, message_id: str, user_id: int) -> Tuple[Message, Conversation]:
        """
        Get a message along with its conversation for additional context.
        
        Args:
            message_id: ID of the message
            user_id: ID of the user (for security)
            
        Returns:
            Tuple of (message, conversation)
        """
        message = self.get_message(message_id, user_id)
        conversation = self.verify_user_owns_conversation(user_id, message.conversation_id)
        
        return message, conversation 