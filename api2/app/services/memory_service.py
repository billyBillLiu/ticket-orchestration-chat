from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Tuple
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
import json

class MemoryService:
    """
    Service for managing conversation memory and context.
    Handles loading conversation history, managing context windows, and memory operations.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_conversation_context(
        self, 
        conversation_id: int, 
        user_id: int, 
        max_messages: int = 20,
        include_system_messages: bool = True
    ) -> Tuple[List[Dict], Optional[str]]:
        """
        Get conversation context for AI processing.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for security)
            max_messages: Maximum number of messages to include in context
            include_system_messages: Whether to include system messages
            
        Returns:
            Tuple of (messages_list, conversation_title)
        """
        try:
            # Verify conversation belongs to user
            conversation = self.db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            ).first()
            
            if not conversation:
                return [], None
            
            # Get messages for this conversation, ordered by creation time
            messages = self.db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at.asc()).limit(max_messages).all()
            
            # Convert to OpenAI-style format
            context_messages = []
            for msg in messages:
                # Skip system messages if not requested
                if not include_system_messages and msg.role == "system":
                    continue
                    
                context_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            return context_messages, conversation.title
            
        except Exception as e:
            print(f"Error getting conversation context: {e}")
            return [], None
    
    def get_conversation_summary(self, conversation_id: int, user_id: int) -> Dict:
        """
        Get a summary of conversation statistics.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for security)
            
        Returns:
            Dictionary with conversation summary
        """
        try:
            # Verify conversation belongs to user
            conversation = self.db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            ).first()
            
            if not conversation:
                return {}
            
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
            
            # Get first and last message timestamps
            first_message = self.db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at.asc()).first()
            
            last_message = self.db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at.desc()).first()
            
            return {
                "conversation_id": conversation_id,
                "title": conversation.title,
                "total_messages": total_messages,
                "user_messages": user_messages,
                "assistant_messages": assistant_messages,
                "created_at": conversation.created_at.isoformat(),
                "updated_at": conversation.updated_at.isoformat(),
                "first_message_at": first_message.created_at.isoformat() if first_message else None,
                "last_message_at": last_message.created_at.isoformat() if last_message else None
            }
            
        except Exception as e:
            print(f"Error getting conversation summary: {e}")
            return {}
    
    def get_user_conversation_memory(self, user_id: int, limit: int = 10) -> List[Dict]:
        """
        Get recent conversation memory for a user.
        Useful for showing recent conversations or context.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of conversations to return
            
        Returns:
            List of conversation summaries
        """
        try:
            conversations = self.db.query(Conversation).filter(
                Conversation.user_id == user_id,
                Conversation.is_archived == False
            ).order_by(Conversation.updated_at.desc()).limit(limit).all()
            
            memory = []
            for conv in conversations:
                summary = self.get_conversation_summary(conv.id, user_id)
                if summary:
                    memory.append(summary)
            
            return memory
            
        except Exception as e:
            print(f"Error getting user conversation memory: {e}")
            return []
    
    def search_conversation_memory(
        self, 
        user_id: int, 
        query: str, 
        limit: int = 10
    ) -> List[Dict]:
        """
        Search through conversation memory for specific content.
        
        Args:
            user_id: ID of the user
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching messages with conversation context
        """
        try:
            # Search in messages content
            messages = self.db.query(Message).join(Conversation).filter(
                Conversation.user_id == user_id,
                Message.content.ilike(f"%{query}%")
            ).order_by(Message.created_at.desc()).limit(limit).all()
            
            results = []
            for msg in messages:
                results.append({
                    "message_id": msg.message_id,
                    "conversation_id": msg.conversation_id,
                    "conversation_title": msg.conversation.title,
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                    "matched_query": query
                })
            
            return results
            
        except Exception as e:
            print(f"Error searching conversation memory: {e}")
            return []
    
    def get_conversation_timeline(self, conversation_id: int, user_id: int) -> List[Dict]:
        """
        Get a timeline of messages in a conversation.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user (for security)
            
        Returns:
            List of messages with timeline information
        """
        try:
            # Verify conversation belongs to user
            conversation = self.db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            ).first()
            
            if not conversation:
                return []
            
            # Get all messages ordered by time
            messages = self.db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at.asc()).all()
            
            timeline = []
            for i, msg in enumerate(messages):
                timeline.append({
                    "index": i + 1,
                    "message_id": msg.message_id,
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                    "is_user": msg.role == "user"
                })
            
            return timeline
            
        except Exception as e:
            print(f"Error getting conversation timeline: {e}")
            return []
    
    def cleanup_old_conversations(self, user_id: int, days_old: int = 30) -> int:
        """
        Archive old conversations to free up memory.
        
        Args:
            user_id: ID of the user
            days_old: Number of days after which to archive conversations
            
        Returns:
            Number of conversations archived
        """
        try:
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Find old conversations
            old_conversations = self.db.query(Conversation).filter(
                Conversation.user_id == user_id,
                Conversation.updated_at < cutoff_date,
                Conversation.is_archived == False
            ).all()
            
            # Archive them
            archived_count = 0
            for conv in old_conversations:
                conv.is_archived = True
                archived_count += 1
            
            self.db.commit()
            return archived_count
            
        except Exception as e:
            print(f"Error cleaning up old conversations: {e}")
            self.db.rollback()
            return 0 