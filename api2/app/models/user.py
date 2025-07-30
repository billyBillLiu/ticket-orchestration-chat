from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(100))
    avatar = Column(String(255))
    role = Column(String(20), default="USER")  # USER, ADMIN
    provider = Column(String(20), default="local")  # local, google, discord, etc.
    email_verified = Column(Boolean, default=True) # TODO: change to false when adding back verification
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Additional fields from Node.js model
    plan = Column(String(20), default="free")
    phone = Column(String(20))
    discord_id = Column(String(255))
    google_id = Column(String(255))
    openai_id = Column(String(255))
    github_id = Column(String(255))
    telegram_id = Column(String(255))
    two_factor_secret = Column(String(255))
    two_factor_enabled = Column(Boolean, default=False)
    refresh_token = Column(Text)
    token_version = Column(Integer, default=0)
    
    # Relationship to conversations
    conversations = relationship("Conversation", back_populates="user") 