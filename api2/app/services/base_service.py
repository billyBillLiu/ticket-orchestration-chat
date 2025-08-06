from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.conversation import Conversation

class BaseService:
    def __init__(self, db: Session):
        self.db = db
    
    def verify_user_owns_conversation(self, user_id: int, conversation_id: int) -> Conversation:
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation