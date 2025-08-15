from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List, Union

class MessageBase(BaseModel):
    content: str
    role: str = Field(..., description="Role of the message sender (user/assistant)")
    conversation_id: Optional[int] = None
    parent_message_id: Optional[str] = None
    is_created_by_user: bool = False

class MessageCreate(MessageBase):
    pass

class MessageUpdate(BaseModel):
    content: Optional[str] = None
    role: Optional[str] = None
    is_created_by_user: Optional[bool] = None

class MessageResponse(BaseModel):
    messageId: str = Field(..., alias="message_id")
    conversationId: str = Field(..., alias="conversation_id")
    parentMessageId: Optional[str] = Field(None, alias="parent_message_id")
    sender: str = Field(..., alias="role")
    text: str = Field(..., alias="content")
    isCreatedByUser: bool = Field(..., alias="is_created_by_user")
    createdAt: datetime = Field(..., alias="created_at")
    updatedAt: Optional[datetime] = Field(None, alias="updated_at")
    unfinished: bool = False
    error: bool = False
    isEdited: bool = False
    model: Optional[str] = None
    endpoint: str = "custom"

    @field_validator('messageId', 'conversationId', mode='before')
    @classmethod
    def convert_to_string(cls, v):
        if v is not None:
            return str(v)
        return v

    class Config:
        from_attributes = True
        populate_by_name = True

class MessageListResponse(BaseModel):
    messages: List[MessageResponse]
    total: int

class ConversationWithMessages(BaseModel):
    conversation: dict
    messages: List[MessageResponse] 