from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(255), unique=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    parent_message_id = Column(String(255), nullable=True)
    role = Column(String(50))  # "user" or "assistant"
    content = Column(Text)
    is_created_by_user = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    conversation = relationship("Conversation", back_populates="messages") 