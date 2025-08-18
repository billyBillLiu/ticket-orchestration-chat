from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.models import get_db
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.routes.auth import get_current_user
import uuid
from datetime import datetime
import json
import logging
from app.utils.response_utils import ApiResponse
from app.constants import DEFAULT_MODEL, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS, DEFAULT_SENDER, DEFAULT_ENDPOINT, DEFAULT_PARENT_MESSAGE_ID

logger = logging.getLogger(__name__)

router = APIRouter()



@router.get("/endpoints")
async def get_endpoints():
    """Get available endpoints configuration"""
    endpoints_data = {
        "custom": {
            "enabled": True,
            "available": True,
            "models": [DEFAULT_MODEL, "llama2:7b", "mistral:7b"]
        },
        "openAI": {
            "enabled": False,
            "available": False,
            "models": ["gpt-3.5-turbo", "gpt-4"]
        },
        "anthropic": {
            "enabled": False,
            "available": False,
            "models": ["claude-3-sonnet", "claude-3-haiku"]
        },
        "google": {
            "enabled": False,
            "available": False,
            "models": []
        },
        "azure": {
            "enabled": False,
            "available": False,
            "models": []
        }
    }
    return endpoints_data

@router.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {"message": "Test endpoint works!"}

@router.get("/llm/health")
async def llm_health_check():
    """Check if LLM service (Ollama) is running"""
    from app.services.llm_service import llm_service
    try:
        is_healthy = await llm_service.health_check()
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "llm_provider": "ollama",
            "base_url": llm_service.base_url,
            "default_model": llm_service.default_model
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "llm_provider": "ollama"
        }

@router.get("/llm/models")
async def list_llm_models():
    """List available LLM models"""
    from app.services.llm_service import llm_service
    try:
        models = await llm_service.list_models()
        return {
            "models": models,
            "default_model": llm_service.default_model
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
            "model": None,
            "endpoint": "ollama"
        })
    
    return result

@router.post("/ask/custom")
async def ask_custom(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        data = await request.json()
        
        # Try to get OpenAI-style messages array
        messages = data.get("messages")
        model = data.get("model", DEFAULT_MODEL)  # Use our actual Ollama model

        # If not present, try to convert from flat format
        if not messages:
            # Check for 'text' and 'sender' fields (LibreChat flat format)
            if "text" in data and "sender" in data:
                messages = [{
                    "role": "user" if data.get("sender", "").lower() == "user" else "assistant",
                    "content": data.get("text", "")
                }]
                model = data.get("model", DEFAULT_MODEL)  # Use our actual Ollama model
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
            # Ensure we use the correct model name
            if model != DEFAULT_MODEL:
                logger.info(f"Model '{model}' not found, using default '{DEFAULT_MODEL}'")
                model = DEFAULT_MODEL
            
            # Log LLM call
            logger.info(f"Calling LLM service with model: '{model}'")
                
        except Exception as e:
            logger.error(f"LLM service error: {e}")
            raise HTTPException(status_code=500, detail=f"LLM service error: {str(e)}")
        
        # Get parent message ID from request
        parent_message_id = data.get("parentMessageId", DEFAULT_PARENT_MESSAGE_ID)
        
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
            "endpoint": "custom"  # Use "custom" instead of DEFAULT_ENDPOINT
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
            
            try:
                # Stream the LLM response
                async for chunk in llm_service.generate_response(
                    messages=llm_messages,
                    model=model,
                    temperature=DEFAULT_TEMPERATURE,
                    max_tokens=DEFAULT_MAX_TOKENS
                ):
                    # Add chunk to accumulated content
                    response_content += chunk
                    
                    # Create streaming response message with accumulated content
                    streaming_response = {
                        "messageId": assistant_message_id,
                        "conversationId": str(conversation.id),
                        "parentMessageId": user_message_id,
                        "sender": DEFAULT_SENDER,
                        "text": response_content,  # Send accumulated content (frontend expects this)
                        "isCreatedByUser": False,
                        "createdAt": assistant_msg.created_at.isoformat() if assistant_msg.created_at else datetime.now().isoformat(),
                        "updatedAt": datetime.now().isoformat(),
                        "model": model,
                        "endpoint": "custom",
                        "unfinished": True,  # Mark as unfinished during streaming
                        "error": False,
                        "isEdited": False
                    }
                    
                    # Send immediately without buffering
                    yield f"event: message\ndata: {json.dumps(streaming_response)}\n\n"
                
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
                    "sender": DEFAULT_SENDER,
                    "text": response_content,  # Send complete content in final message
                    "isCreatedByUser": False,
                    "createdAt": assistant_msg.created_at.isoformat() if assistant_msg.created_at else datetime.now().isoformat(),
                    "updatedAt": datetime.now().isoformat(),
                    "model": model,
                    "endpoint": "custom",
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
                        "endpoint": "custom",
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
                    "sender": DEFAULT_SENDER,
                    "text": f"I'm having trouble processing your request right now. Please try again. Your message was: {user_message}",
                    "isCreatedByUser": False,
                    "createdAt": datetime.now().isoformat(),
                    "updatedAt": datetime.now().isoformat(),
                    "model": model,
                    "endpoint": "custom",
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
        print(f"Error in ask_custom: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 