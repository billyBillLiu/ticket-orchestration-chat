# app/routes/agents.py
from __future__ import annotations
import uuid
from fastapi import APIRouter, HTTPException
from app.models.ticket_agent import ConversationState, ChatTurn
from app.schemas.agent_io import StartSessionOut, ChatMessageIn, ChatMessageOut, QuestionOut
from app.services.planner_service import plan_from_text
from app.services.validator_service import find_missing_fields, render_question, apply_answer
from app.services.summary_service import generate_summaries_for_plan
from app.utils.session_store import put, get

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/start", response_model=StartSessionOut)
def start_session():
    """
    Creates an empty conversation state and returns a session_id.
    Your frontend should call this once per chat session.
    """
    sid = str(uuid.uuid4())
    state = ConversationState(session_id=sid)
    put(state)
    return StartSessionOut(session_id=sid)

@router.post("/{sid}/message", response_model=ChatMessageOut)
async def chat_message(sid: str, payload: ChatMessageIn):
    """
    Core loop:
    - If there's no plan yet, create one from the user's first message.
    - If this message is an answer to a previous question, apply it.
    - Find the next missing required field; if any, ask a follow-up question.
    - If no missing fields, "create tickets" (mock) and return a summary.
    """
    state = get(sid)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")

    # Record the user turn for audit/debug
    state.turns.append(ChatTurn(role="user", text=payload.text))

    # If the user is answering a specific field question, store the answer
    if payload.answer_to:
        idx = int(payload.answer_to["item_index"])
        fname = str(payload.answer_to["field_name"])
        # NOTE: your UI should send the correct type:
        # - multi_choice => list[str]
        # - date/time => ISO strings
        # - files => array of uploaded file refs (your uploader decides the shape)
        state.plan = apply_answer(state.plan, idx, fname, payload.text)  # change this to payload.value if you prefer

    # If we don't have a plan yet, create one now from the first user utterance
    if state.plan is None:
        plan = plan_from_text(payload.text, payload.user_email)
        # Add minimal meta (you can attach requester / target from payload.context)
        plan.meta = {"request_text": payload.text, **(payload.context or {})}
        state.plan = plan
        
        # Directly set the user's email in all ticket forms
        if payload.user_email:
            print(f"📧 AGENT: Setting user email '{payload.user_email}' in all ticket forms")
            for item in state.plan.items:
                if "email" in item.form:
                    item.form["email"] = payload.user_email
                    print(f"📧 AGENT: Set email for {item.ticket_type}")

    # Compute which required fields are missing
    missing = find_missing_fields(state.plan)
    state.pending = missing

    if missing:
        # Ask for the next field and return it to the UI
        q = render_question(missing[0])
        state.turns.append(ChatTurn(role="assistant", text=q["text"]))
        put(state)
        return ChatMessageOut(
            session_id=sid,
            status="need_more_info",
            question=QuestionOut(**q),
            plan_preview=state.plan.model_dump()
        )

    # Otherwise, we have a complete plan—generate summaries and "create" tickets (mock)
    print(f"📝 AGENT: All fields filled, generating summaries...")
    state.plan = await generate_summaries_for_plan(state.plan)
    
    state.completed = True
    created = [
        {
            "pseudo_id": f"{it.service_area.split()[0][:3].upper()}-{1000+i}",
            "service_area": it.service_area,
            "category": it.category,
            "ticket_type": it.ticket_type,
            "title": it.title,
            "form": it.form
        }
        for i, it in enumerate(state.plan.items)
    ]
    state.turns.append(ChatTurn(role="assistant", text="Tickets created with auto-generated summaries."))
    put(state)

    return ChatMessageOut(
        session_id=sid,
        status="done",
        result={"created": created},
        plan=state.plan.model_dump()
    )
