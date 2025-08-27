# app/utils/session_store.py
from __future__ import annotations
from typing import Dict
from app.models.ticket_agent import ConversationState

# WARNING: This is per-process memory. Use Redis or DB in production/multi-worker setups.
_SESSIONS: Dict[str, ConversationState] = {}

def put(state: ConversationState):
    _SESSIONS[state.session_id] = state

def get(session_id: str) -> ConversationState | None:
    return _SESSIONS.get(session_id)

def delete(session_id: str):
    _SESSIONS.pop(session_id, None)
