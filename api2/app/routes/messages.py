from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.models import get_db
from app.models.user import User
from app.schemas.message import MessageResponse, MessageCreate, MessageUpdate, MessageListResponse
from app.routes.auth import get_current_user
from app.services.message_service import MessageService

# Import agentic ticket creation components
from app.services.planner_service import plan_from_text
from app.services.validator_service import find_missing_fields, render_question, apply_answer
from app.services.summary_service import generate_summaries_for_plan
from app.models.ticket_agent import ConversationState, ChatTurn
from app.utils.session_store import put, get

router = APIRouter(tags=["Messages"])

def is_ticket_request(content: str) -> bool:
    """Detect if the user message is requesting ticket creation"""
    ticket_keywords = [
        "create ticket", "new ticket", "submit ticket", "open ticket",
        "support request", "help request", "incident report", "bug report",
        "datadog", "sftp", "jams", "monitoring", "alert", "dashboard",
        "loan tape", "investor", "rerun", "verification"
    ]
    content_lower = content.lower()
    return any(keyword in content_lower for keyword in ticket_keywords)

async def handle_agentic_ticket_creation(content: str, conversation_id: int, user_email: str = None) -> dict:
    """Handle ticket creation using the agentic flow"""
    # Create or get session for this conversation
    session_id = f"conv_{conversation_id}"
    state = get(session_id)
    
    if not state:
        state = ConversationState(session_id=session_id)
        put(state)
    
    # Record the user turn
    state.turns.append(ChatTurn(role="user", text=content))
    
    # If no plan yet, create one
    if state.plan is None:
        state.plan = plan_from_text(content, user_email)
        state.plan.meta = {"request_text": content, "conversation_id": conversation_id}
        
        # Directly set the user's email in all ticket forms
        if user_email:
            print(f"📧 AGENT: Setting user email '{user_email}' in all ticket forms")
            for item in state.plan.items:
                if "email" in item.form:
                    item.form["email"] = user_email
                    print(f"📧 AGENT: Set email for {item.ticket_type}")
    
    # Find missing fields
    missing = find_missing_fields(state.plan)
    state.pending = missing
    
    if missing:
        # Ask for next field
        question = render_question(missing[0])
        state.turns.append(ChatTurn(role="assistant", text=question["text"]))
        put(state)
        
        return {
            "type": "agent_question",
            "content": question["text"],
            "question": question,
            "plan_preview": state.plan.model_dump(),
            "session_id": session_id
        }
    else:
        # Complete - generate summaries and create tickets
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
        state.turns.append(ChatTurn(role="assistant", text="Tickets created successfully with auto-generated summaries!"))
        put(state)
        
        return {
            "type": "agent_complete",
            "content": f"✅ Created {len(created)} ticket(s):\n" + "\n".join([f"• {t['title']} ({t['pseudo_id']})" for t in created]),
            "tickets": created,
            "plan": state.plan.model_dump()
        }

@router.get("/{conversation_id}/messages", response_model=MessageListResponse)
async def get_conversation_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100)
):
    """
    Get all messages for a specific conversation.
    Supports pagination and ensures user can only access their own conversations.
    """
    try:
        message_service = MessageService(db)
        messages, total = message_service.get_conversation_messages(
            conversation_id, current_user.id, page, limit
        )
        
        # Convert to response models
        message_responses = [MessageResponse.model_validate(msg) for msg in messages]
        
        return MessageListResponse(
            messages=message_responses,
            total=total
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching messages: {str(e)}"
        )

@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def create_message(
    conversation_id: int,
    message: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new message in a conversation.
    If the message appears to be a ticket request, use the agentic flow.
    """
    try:
        # Check if this is a ticket request
        if is_ticket_request(message.content):
            # Handle with agentic ticket creation
            agent_response = await handle_agentic_ticket_creation(message.content, conversation_id, current_user.email)
            
            # Create the user message normally
            message_service = MessageService(db)
            user_message = message_service.create_message(
                conversation_id, current_user.id, message
            )
            
            # Create the assistant response
            assistant_message_data = MessageCreate(
                content=agent_response["content"],
                role="assistant",
                conversation_id=conversation_id,
                parent_message_id=user_message.message_id,
                is_created_by_user=False
            )
            
            assistant_message = message_service.create_message(
                conversation_id, current_user.id, assistant_message_data
            )
            
            # Add agent metadata to the response
            response = MessageResponse.model_validate(assistant_message)
            response.model = "ticket-agent"
            response.endpoint = "agentic-ticket-creation"
            
            # Include agent data in the response
            response_data = response.model_dump()
            response_data["agent_data"] = agent_response
            
            return response_data
        
        else:
            # Normal message flow
            message_service = MessageService(db)
            new_message = message_service.create_message(
                conversation_id, current_user.id, message
            )
            
            return MessageResponse.model_validate(new_message)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating message: {str(e)}"
        )

@router.get("/messages/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific message by ID.
    """
    try:
        message_service = MessageService(db)
        message = message_service.get_message(message_id, current_user.id)
        
        return MessageResponse.model_validate(message)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching message: {str(e)}"
        )

@router.put("/messages/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: str,
    message_update: MessageUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a specific message.
    """
    try:
        message_service = MessageService(db)
        updated_message = message_service.update_message(
            message_id, current_user.id, message_update
        )
        
        return MessageResponse.model_validate(updated_message)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating message: {str(e)}"
        )

@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific message.
    """
    try:
        message_service = MessageService(db)
        message_service.delete_message(message_id, current_user.id)
        
        return {"message": "Message deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting message: {str(e)}"
        ) 

@router.post("/{conversation_id}/agent-answer")
async def answer_agent_question(
    conversation_id: int,
    answer_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Answer a question from the agentic ticket creation flow.
    """
    try:
        session_id = answer_data.get("session_id")
        question = answer_data.get("question")
        answer = answer_data.get("answer")
        
        if not all([session_id, question, answer]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required fields: session_id, question, answer"
            )
        
        # Get the agent state
        state = get(session_id)
        if not state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent session not found"
            )
        
        # Apply the answer
        item_index = question["item_index"]
        field_name = question["field_name"]
        state.plan = apply_answer(state.plan, item_index, field_name, answer)
        
        # Record the user turn
        state.turns.append(ChatTurn(role="user", text=answer))
        
        # Find next missing field
        missing = find_missing_fields(state.plan)
        state.pending = missing
        
        if missing:
            # Ask for next field
            next_question = render_question(missing[0])
            state.turns.append(ChatTurn(role="assistant", text=next_question["text"]))
            put(state)
            
            return {
                "type": "agent_question",
                "content": next_question["text"],
                "question": next_question,
                "plan_preview": state.plan.model_dump(),
                "session_id": session_id
            }
        else:
            # Complete - create tickets
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
            state.turns.append(ChatTurn(role="assistant", text="Tickets created successfully!"))
            put(state)
            
            return {
                "type": "agent_complete",
                "content": f"✅ Created {len(created)} ticket(s):\n" + "\n".join([f"• {t['title']} ({t['pseudo_id']})" for t in created]),
                "tickets": created,
                "plan": state.plan.model_dump()
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing agent answer: {str(e)}"
        ) 