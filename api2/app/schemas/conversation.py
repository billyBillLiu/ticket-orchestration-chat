from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List, Union

class ConversationBase(BaseModel):
    title: Optional[str] = None
    isArchived: bool = Field(False, alias="is_archived")

class ConversationCreate(ConversationBase):
    pass

class ConversationUpdate(ConversationBase):
    title: Optional[str] = None
    isArchived: Optional[bool] = Field(None, alias="is_archived")

class ConversationResponse(BaseModel):
    conversationId: str = Field(..., alias="id")
    title: Optional[str] = None
    user: str = Field(..., alias="user_id")
    createdAt: datetime = Field(..., alias="created_at")
    updatedAt: datetime = Field(..., alias="updated_at")
    isArchived: bool = Field(False, alias="is_archived")

    @field_validator('conversationId', 'user', mode='before')
    @classmethod
    def convert_to_string(cls, v):
        if v is not None:
            return str(v)
        return v

    class Config:
        from_attributes = True
        populate_by_name = True

class ConversationListResponse(BaseModel):
    conversations: List[ConversationResponse]
    total: int 