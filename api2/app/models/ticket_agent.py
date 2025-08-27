# app/models/agent.py
from __future__ import annotations
from pydantic import BaseModel
from typing import Any, Dict, List, Literal, Optional

# ---- FieldDef describes a single form field for a ticket spec ----
class FieldDef(BaseModel):
    name: str
    type: Literal["string", "rich_text", "bool", "int", "date", "time", "file", "files", "choice", "multi_choice"]
    description: str = ""
    options: Optional[List[str]] = None
    options_source: Optional[str] = None
    required: Optional[bool] = None

# ---- TicketSpec is the "template" (from catalog) for a ticket type ----
class TicketSpec(BaseModel):
    service_area: str      # e.g., "SRE/Production Support"
    category: str          # e.g., "IT Service Requests"
    ticket_type: str       # e.g., "Datadog Log Rehydration"
    description: str = ""
    fields: List[FieldDef]

# ---- TicketItem is a concrete, planned ticket instance ----
class TicketItem(BaseModel):
    service_area: str
    category: str
    ticket_type: str
    title: str             # short, action-oriented; used in lists
    description: str       # concise context for the executor/assignee
    form: Dict[str, Any] = {}   # collected answers keyed by FieldDef.name
    labels: List[str] = []      # e.g., ["needs-triage"]

# ---- TicketPlan is the full plan the agent intends to execute ----
class TicketPlan(BaseModel):
    items: List[TicketItem]
    meta: Dict[str, Any]       # audit info: {"request_text": "...", ...}

# ---- MissingField links a specific TicketItem to a field that needs value ----
class MissingField(BaseModel):
    item_index: int            # index inside TicketPlan.items
    field: FieldDef            # the field definition (type/options/desc)

# ---- ChatTurn captures the dialog transcript (for audit/debug) ----
class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    text: str

# ---- ConversationState keeps everything together per session ----
class ConversationState(BaseModel):
    session_id: str
    turns: List[ChatTurn] = []
    plan: Optional[TicketPlan] = None
    pending: List[MissingField] = []   # queue of unanswered fields
    completed: bool = False
