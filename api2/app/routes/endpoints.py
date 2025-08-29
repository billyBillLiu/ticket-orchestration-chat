from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.models import get_db
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.routes.auth import get_current_user
import uuid
import asyncio
from datetime import datetime
import json
import logging
from app.utils.response_utils import ApiResponse
from app.config import settings
from app.constants import ACTIVE_MODEL, ACTIVE_PROVIDER

# Import agentic ticket creation components
from app.services.planner_service import plan_from_text, plan_from_text_async
from app.services.validator_service import find_missing_fields, render_question, apply_answer, apply_answer_async
from app.services.summary_service import generate_summaries_for_plan
from app.models.ticket_agent import ConversationState, ChatTurn
from app.utils.session_store import put, get

logger = logging.getLogger(__name__)

def is_ticket_request(content: str, conversation_id: int = None) -> bool:
    """Detect if the user message is requesting ticket creation or continuing an agent session"""
    # First check if there's an active agent session for this conversation
    if conversation_id is not None:
        session_id = f"conv_{conversation_id}"
        state = get(session_id)
        if state and not state.completed:
            print(f"🎯 AGENT: Found active session {session_id} with {len(state.pending)} pending questions")
            return True
    
    # Then check for ticket-related keywords
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
    print(f"🎯 AGENT: Starting agentic ticket creation for conversation {conversation_id}")
    print(f"💬 AGENT: User content: '{content}'")
    
    # Create or get session for this conversation
    session_id = f"conv_{conversation_id}"
    state = get(session_id)
    
    if not state:
        print(f"🆕 AGENT: Creating new session: {session_id}")
        state = ConversationState(session_id=session_id)
        put(state)
    else:
        print(f"📂 AGENT: Using existing session: {session_id}")
    
    # Record the user turn
    state.turns.append(ChatTurn(role="user", text=content))
    print(f"📝 AGENT: Recorded user turn, total turns: {len(state.turns)}")
    
    # If no plan yet, create one
    if state.plan is None:
        print(f"📋 AGENT: No plan exists, creating new plan...")
        state.plan = await plan_from_text_async(content, user_email)
        state.plan.meta = {"request_text": content, "conversation_id": conversation_id}
         
        # Directly set the user's email in all ticket forms
        if user_email:
            print(f"📧 AGENT: Setting user email '{user_email}' in all ticket forms")
            for item in state.plan.items:
                if "email" in item.form:
                    item.form["email"] = user_email
                    print(f"📧 AGENT: Set email for {item.ticket_type}")
        
        print(f"✅ AGENT: Plan created with {len(state.plan.items)} items")
    else:
        print(f"📋 AGENT: Using existing plan with {len(state.plan.items)} items")
        # User is answering a question, so apply the answer
        if state.pending:
            print(f"📝 AGENT: User is answering question for field: {state.pending[0].field.name}")
            missing_field = state.pending[0]
            state.plan = await apply_answer_async(state.plan, missing_field.item_index, missing_field.field.name, content)
            state.turns.append(ChatTurn(role="user", text=content))
            print(f"✅ AGENT: Applied answer to plan")
    
    # Find missing fields
    print(f"🔍 AGENT: Finding missing fields...")
    missing = find_missing_fields(state.plan)
    state.pending = missing
    print(f"📊 AGENT: Found {len(missing)} missing fields")
    
    if missing:
        # Ask for next field
        print(f"❓ AGENT: Asking for field: {missing[0].field.name}")
        question = render_question(missing[0])
        state.turns.append(ChatTurn(role="assistant", text=question["text"]))
        put(state)
        
        print(f"✅ AGENT: Returning agent question")
        return {
            "type": "agent_question",
            "content": question["text"],
            "question": question,
            "plan_preview": state.plan.model_dump(),
            "session_id": session_id
        }
    else:
        # Complete - generate summaries and create tickets
        print(f"🎉 AGENT: All fields complete, generating summaries...")
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
        
        print(f"✅ AGENT: Created {len(created)} tickets")
        
        # Create detailed content with full JSON
        content_lines = [f"✅ Created {len(created)} ticket(s):"]
        for i, ticket in enumerate(created):
            content_lines.append(f"\n**Ticket {i+1}: {ticket['title']} ({ticket['pseudo_id']})**")
            content_lines.append(f"Service Area: {ticket['service_area']}")
            content_lines.append(f"Category: {ticket['category']}")
            content_lines.append(f"Type: {ticket['ticket_type']}")
            content_lines.append("Form Data:")
            content_lines.append("```json")
            content_lines.append(json.dumps(ticket['form'], indent=2))
            content_lines.append("```")
        
        content_lines.append(f"\n**Complete Plan JSON:**")
        content_lines.append("```json")
        content_lines.append(json.dumps(state.plan.model_dump(), indent=2))
        content_lines.append("```")
        
        return {
            "type": "agent_complete",
            "content": "\n".join(content_lines),
            "tickets": created,
            "plan": state.plan.model_dump()
        }

router = APIRouter()

@router.get("/endpoints")
async def get_endpoints():
    """Get available endpoints configuration - simplified for single model"""
    # Use "custom" as the endpoint key for compatibility
    endpoint_key = "custom"
    endpoints_data = {
        endpoint_key: {
            "enabled": True,
            "available": True,
            "models": [settings.llm_model]  # Only the active model
        }
    }
    return endpoints_data

@router.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {"message": "Test endpoint works!"}

@router.get("/llm/health")
async def llm_health_check():
    """Check if LLM service is running"""
    from app.services.llm_service import llm_service
    try:
        is_healthy = await llm_service.health_check()
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "llm_provider": llm_service.provider,
            "base_url": llm_service.base_url,
            "default_model": llm_service.model
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "llm_provider": llm_service.provider
        }

@router.get("/llm/models")
async def list_llm_models():
    """List available LLM models - simplified for single model"""
    from app.services.llm_service import llm_service
    try:
        # Return only the active model instead of all available models
        return {
            "models": [{"name": llm_service.model}],  # Single model only
            "default_model": llm_service.model
        }
    except Exception as e:
        return {
            "error": str(e),
            "models": []
        }

@router.get("/messages/{conversation_id}")
async def get_messages(conversation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get messages for a conversation"""
    # Convert conversation_id to int if it's a number
    try:
        conv_id = int(conversation_id)
    except ValueError:
        return []
    
    # Get messages for this conversation
    messages = db.query(Message).filter(Message.conversation_id == conv_id).order_by(Message.created_at).all()
    
    # Convert to the format expected by the frontend
    result = []
    for msg in messages:
        # Get conversation to get model info
        conversation = db.query(Conversation).filter(Conversation.id == msg.conversation_id).first()
        model = conversation.model if conversation else ACTIVE_MODEL
        endpoint = conversation.endpoint if conversation else ACTIVE_PROVIDER
        
        result.append({
            "messageId": msg.message_id,
            "conversationId": str(msg.conversation_id),
            "parentMessageId": msg.parent_message_id or "00000000-0000-0000-0000-000000000000",
            "sender": msg.role,
            "text": msg.content,
            "isCreatedByUser": msg.is_created_by_user,
            "createdAt": msg.created_at.isoformat(),
            "updatedAt": msg.updated_at.isoformat() if msg.updated_at is not None else msg.created_at.isoformat(),
            "unfinished": False,
            "error": False,
            "isEdited": False,
            "model": model,
            "endpoint": endpoint
        })
    
    return result

@router.post("/ask/{provider}")
async def ask_provider(provider: str, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Ask the configured LLM provider - simplified for single model"""
    # Accept "custom" as a valid provider that maps to the configured provider
    if provider == "custom":
        provider = settings.llm_provider
    elif provider != settings.llm_provider:
        raise HTTPException(
            status_code=400, 
            detail=f"Provider '{provider}' not configured. Using '{settings.llm_provider}'"
        )
    
    try:
        data = await request.json()
        
        # Try to get OpenAI-style messages array
        messages = data.get("messages")
        # Always use the configured model - no model selection
        model = settings.llm_model

        # If not present, try to convert from flat format
        if not messages:
            # Check for 'text' and 'sender' fields (LibreChat flat format)
            if "text" in data and "sender" in data:
                messages = [{
                    "role": "user" if data.get("sender", "").lower() == "user" else "assistant",
                    "content": data.get("text", "")
                }]
                # Always use the configured model
                model = settings.llm_model
            else:
                raise HTTPException(status_code=400, detail="No messages provided")

        # Check if we should continue an existing conversation or create a new one
        conversation_id = data.get("conversationId")
        conversation = None  # Initialize conversation variable
        
        if conversation_id and conversation_id != "00000000-0000-0000-0000-000000000000":
            # Try to find existing conversation
            try:
                conv_id = int(conversation_id)
                conversation = db.query(Conversation).filter(
                    Conversation.id == conv_id,
                    Conversation.user_id == current_user.id
                ).first()
            except (ValueError, TypeError):
                conversation = None
        
        if not conversation:
            # Create a new conversation using the service
            from app.services.conversation_service import ConversationService
            conversation_service = ConversationService(db)
            conversation = conversation_service.create_conversation(current_user.id)

        # Mock OpenAI-like response
        response_id = str(uuid.uuid4())
        user_message = messages[-1]["content"] if messages else ""
        
        # Check if this is a ticket request and handle with agentic flow
        if is_ticket_request(user_message, conversation.id):
            logger.info(f"🎫 Detected ticket request: '{user_message}'")
            
            # Handle with agentic ticket creation
            agent_response = await handle_agentic_ticket_creation(user_message, conversation.id, current_user.email)
            
            # Create the user message in database
            user_message_id = str(uuid.uuid4())
            parent_message_id = data.get("parentMessageId", "00000000-0000-0000-0000-000000000000")
            
            user_msg = Message(
                message_id=user_message_id,
                conversation_id=conversation.id,
                parent_message_id=parent_message_id,
                role="user",
                content=user_message,
                is_created_by_user=True
            )
            db.add(user_msg)
            db.commit()
            
            # Note: We'll create the assistant message in the streaming function to avoid duplicate insertion
            
            # Create the request message for the frontend
            request_message = {
                "messageId": user_message_id,
                "conversationId": str(conversation.id),
                "parentMessageId": parent_message_id,
                "sender": "user",
                "text": user_message,
                "isCreatedByUser": True,
                "createdAt": user_msg.created_at.isoformat(),
                "updatedAt": user_msg.created_at.isoformat(),
                "unfinished": False,
                "error": False,
                "isEdited": False,
                "model": model,
                "endpoint": "custom"
            }
            
            # Return agentic response as streaming response
            async def generate_agentic_stream():
                # Send the created event first to set up the messages
                created_data = {
                    "created": True,
                    "message": request_message
                }
                yield f"event: message\ndata: {json.dumps(created_data)}\n\n"
                
                # Create the assistant message for agentic response
                assistant_msg = Message(
                    message_id=response_id,
                    conversation_id=conversation.id,
                    parent_message_id=user_message_id,
                    role="assistant",
                    content=agent_response["content"],
                    is_created_by_user=False
                )
                
                # Store the assistant message in database
                try:
                    db.add(assistant_msg)
                    db.commit()
                except Exception as e:
                    db.rollback()
                    logger.error(f"Database error storing assistant message: {e}")
                
                # Send the agentic response message as regular chat (no special agent_data)
                agentic_response = {
                     "messageId": response_id,
                     "conversationId": str(conversation.id),
                     "parentMessageId": user_message_id,
                     "sender": "Ticket Bot",
                     "text": agent_response["content"],
                     "isCreatedByUser": False,
                     "createdAt": assistant_msg.created_at.isoformat() if assistant_msg.created_at else datetime.now().isoformat(),
                     "updatedAt": datetime.now().isoformat(),
                     "model": model,
                     "endpoint": "custom",
                     "unfinished": False,
                     "error": False,
                     "isEdited": False
                     # Removed agent_data to make it appear as regular chat
                 }
                
                yield f"event: message\ndata: {json.dumps(agentic_response)}\n\n"
                
                # Send final response data
                final_data = {
                    "final": True,
                    "title": conversation.title,
                    "conversation": {
                        "conversationId": str(conversation.id),
                        "title": conversation.title,
                        "user": str(conversation.user_id),
                        "createdAt": conversation.created_at.isoformat(),
                        "updatedAt": conversation.updated_at.isoformat(),
                        "model": model,
                        "endpoint": "custom",
                        "isArchived": False,
                        "messages": [user_message_id, response_id]
                    },
                    "requestMessage": request_message,
                    "responseMessage": agentic_response
                }
                
                yield f"event: message\ndata: {json.dumps(final_data)}\n\n"
                yield "data: [DONE]\n\n"
            
            return StreamingResponse(
                generate_agentic_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                    "X-Accel-Buffering": "no",
                    "Transfer-Encoding": "chunked",
                }
            )
        
        # Get conversation context for better responses
        from app.services.memory_service import MemoryService
        memory_service = MemoryService(db)
        context_messages, conversation_title = memory_service.get_conversation_context(
            conversation_id=conversation.id,
            user_id=current_user.id,
            max_messages=10  # Limit context to last 10 messages
        )
        
        # Use LLM service to generate actual response
        from app.services.llm_service import llm_service, Message as LLMMessage
        
        # Prepare messages for LLM (include context if available)
        llm_messages = []
        
        # Add system message for ticket orchestration context
        llm_messages.append(LLMMessage(
            role="system",
            content="You are a helpful AI assistant for a support ticket orchestration system. Help users with their issues and guide them through the ticket creation process when needed."
        ))
        
        # Add conversation context if available
        if context_messages:
            for ctx_msg in context_messages[-5:]:  # Last 5 context messages
                llm_messages.append(LLMMessage(
                    role=ctx_msg.get("role", "user"),
                    content=ctx_msg.get("content", "")
                ))
        
        # Add current user message
        llm_messages.append(LLMMessage(
            role="user",
            content=user_message
        ))
        
        # Generate response using LLM
        try:
            # Always use the configured model - no validation needed
            logger.info(f"Calling LLM service with model: '{model}'")
                
        except Exception as e:
            logger.error(f"LLM service error: {e}")
            raise HTTPException(status_code=500, detail=f"LLM service error: {str(e)}")
        
        # Get parent message ID from request
        parent_message_id = data.get("parentMessageId", "00000000-0000-0000-0000-000000000000")
        
        # Create message IDs
        user_message_id = str(uuid.uuid4())
        assistant_message_id = response_id
        
        # Store the user message in the database first
        try:
            user_msg = Message(
                message_id=user_message_id,
                conversation_id=conversation.id,
                parent_message_id=parent_message_id,
                role="user",
                content=user_message,
                is_created_by_user=True
            )
            db.add(user_msg)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Database error storing user message: {e}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        # Create the request message for the frontend
        request_message = {
            "messageId": user_message_id,
            "conversationId": str(conversation.id),
            "parentMessageId": parent_message_id,
            "sender": "user",
            "text": user_message,
            "isCreatedByUser": True,
            "createdAt": user_msg.created_at.isoformat(),
            "updatedAt": user_msg.created_at.isoformat(),
            "unfinished": False,
            "error": False,
            "isEdited": False,
            "model": model,  # Use the actual model instead of None
            "endpoint": "custom"  # Use "custom" for compatibility
        }
        
        # Use FastAPI's async streaming response
        async def generate_async_stream():
            # Send the created event first to set up the messages
            created_data = {
                "created": True,
                "message": request_message
            }
            yield f"event: message\ndata: {json.dumps(created_data)}\n\n"
            
            # Initialize response content
            response_content = ""
            
            # Create a temporary assistant message for streaming
            assistant_msg = Message(
                message_id=assistant_message_id,
                conversation_id=conversation.id,
                parent_message_id=user_message_id,
                role="assistant",
                content="",  # Will be updated as we stream
                is_created_by_user=False
            )
            
            # Don't send assistant message creation event - let messageHandler handle it
            
            try:
                # Stream the LLM response
                async for chunk in llm_service.generate_response(
                    messages=llm_messages,
                    model=model,
                    temperature=settings.default_temperature,
                    max_tokens=settings.default_max_tokens
                ):
                    # Add chunk to accumulated content for final storage
                    response_content += chunk
                    
                    # Create streaming response message with accumulated content
                    # The frontend messageHandler expects the full text to replace the message
                    streaming_response = {
                        "message": True,  # This triggers the messageHandler
                        "messageId": assistant_message_id,
                        "conversationId": str(conversation.id),
                        "parentMessageId": user_message_id,
                        "sender": "Ticket Bot",
                        "text": response_content,  # Send accumulated content (frontend expects this)
                        "isCreatedByUser": False,
                        "createdAt": assistant_msg.created_at.isoformat() if assistant_msg.created_at else datetime.now().isoformat(),
                        "updatedAt": datetime.now().isoformat(),
                        "model": model,
                        "endpoint": "custom",  # Use "custom" for compatibility
                        "unfinished": True,  # Mark as unfinished during streaming
                        "error": False,
                        "isEdited": False
                    }
                    
                    # Send immediately without buffering
                    yield f"event: message\ndata: {json.dumps(streaming_response)}\n\n"
                    # Add a small delay to prevent overwhelming the frontend
                    await asyncio.sleep(0.01)
                
                # Store the complete response in database
                try:
                    assistant_msg.content = response_content
                    db.add(assistant_msg)
                    db.commit()
                except Exception as e:
                    db.rollback()
                    logger.error(f"Database error storing assistant message: {e}")
                
                # Send final response message with complete content
                final_response = {
                    "messageId": assistant_message_id,
                    "conversationId": str(conversation.id),
                    "parentMessageId": user_message_id,
                    "sender": "Ticket Bot",
                    "text": response_content,  # Send complete content in final message
                    "isCreatedByUser": False,
                    "createdAt": assistant_msg.created_at.isoformat() if assistant_msg.created_at else datetime.now().isoformat(),
                    "updatedAt": datetime.now().isoformat(),
                    "model": model,
                    "endpoint": "custom",  # Use "custom" for compatibility
                    "unfinished": False,  # Mark as finished
                    "error": False,
                    "isEdited": False
                }
                
                # Send final response data
                final_data = {
                    "final": True,
                    "title": conversation.title,
                    "conversation": {
                        "conversationId": str(conversation.id),
                        "title": conversation.title,
                        "user": str(conversation.user_id),
                        "createdAt": conversation.created_at.isoformat(),
                        "updatedAt": conversation.updated_at.isoformat(),
                        "model": model,
                        "endpoint": "custom",  # Use "custom" for compatibility
                        "isArchived": False,
                        "messages": [user_message_id, assistant_message_id]
                    },
                    "requestMessage": request_message,
                    "responseMessage": final_response
                }
                
                yield f"event: message\ndata: {json.dumps(final_data)}\n\n"
                yield "data: [DONE]\n\n"
                    
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                # Send error response
                error_response = {
                    "messageId": assistant_message_id,
                    "conversationId": str(conversation.id),
                    "parentMessageId": user_message_id,
                    "sender": "Ticket Bot",
                    "text": f"I'm having trouble processing your request right now. Please try again. Your message was: {user_message}",
                    "isCreatedByUser": False,
                    "createdAt": datetime.now().isoformat(),
                    "updatedAt": datetime.now().isoformat(),
                    "model": model,
                    "endpoint": "custom",  # Use "custom" for compatibility
                    "unfinished": False,
                    "error": True,
                    "isEdited": False
                }
                yield f"event: message\ndata: {json.dumps(error_response)}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate_async_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
                "Transfer-Encoding": "chunked",
            }
        )
        
    except Exception as e:
        print(f"Error in ask_provider: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Keep the old endpoint for backward compatibility
@router.post("/ask/custom")
async def ask_custom(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Legacy endpoint - redirects to the configured provider"""
    return await ask_provider(settings.llm_provider, request, db, current_user)

@router.post("/agent-answer")
async def answer_agent_question(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Answer a question from the agentic ticket creation flow"""
    try:
        data = await request.json()
        session_id = data.get("session_id")
        question = data.get("question")
        answer = data.get("answer")
        
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
        missing_field = state.pending[0] if state.pending else None
        if not missing_field:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No pending questions"
            )
        
        # Apply answer to the plan
        state.plan = await apply_answer_async(state.plan, missing_field.item_index, missing_field.field.name, answer)
        state.turns.append(ChatTurn(role="user", text=answer))
        
        # Check for more missing fields
        missing = find_missing_fields(state.plan)
        state.pending = missing
        
        if missing:
            # Ask next question
            question = render_question(missing[0])
            state.turns.append(ChatTurn(role="assistant", text=question["text"]))
            put(state)
            
            return {
                "type": "agent_question",
                "content": question["text"],
                "question": question,
                "plan_preview": state.plan.model_dump()
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
            
            # Create detailed content with full JSON
            content_lines = [f"✅ Created {len(created)} ticket(s):"]
            for i, ticket in enumerate(created):
                content_lines.append(f"\n**Ticket {i+1}: {ticket['title']} ({ticket['pseudo_id']})**")
                content_lines.append(f"Service Area: {ticket['service_area']}")
                content_lines.append(f"Category: {ticket['category']}")
                content_lines.append(f"Type: {ticket['ticket_type']}")
                content_lines.append("Form Data:")
                content_lines.append("```json")
                content_lines.append(json.dumps(ticket['form'], indent=2))
                content_lines.append("```")
            
            content_lines.append(f"\n**Complete Plan JSON:**")
            content_lines.append("```json")
            content_lines.append(json.dumps(state.plan.model_dump(), indent=2))
            content_lines.append("```")
            
            return {
                "type": "agent_complete",
                "content": "\n".join(content_lines),
                "tickets": created,
                "plan": state.plan.model_dump()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling agent answer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error handling agent answer: {str(e)}"
        ) 