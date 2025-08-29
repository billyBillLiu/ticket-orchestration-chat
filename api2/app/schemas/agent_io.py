# app/schemas/agent_io.py
from __future__ import annotations
from typing import Any, Dict, Optional
from pydantic import BaseModel

class StartSessionOut(BaseModel):
    session_id: str

class ChatMessageIn(BaseModel):
    text: str
    # When answering a follow-up, tell us which field this answer belongs to
    answer_to: Optional[Dict[str, Any]] = None  # {"item_index": int, "field_name": str}
    # Optional context you may pass from your UI (e.g., requester, target employee)
    context: Optional[Dict[str, Any]] = None
    # User's email for auto-filling email fields
    user_email: Optional[str] = None

class QuestionOut(BaseModel):
    text: str
    type: str
    options: Optional[list] = None
    item_index: int
    field_name: str
    description: str

class ChatMessageOut(BaseModel):
    session_id: str
    status: str              # "need_more_info" | "done"
    question: Optional[QuestionOut] = None
    plan_preview: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    plan: Optional[Dict[str, Any]] = None
