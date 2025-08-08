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
from app.utils.response_utils import ApiResponse

router = APIRouter()



@router.get("/endpoints")
async def get_endpoints():
    """Get available endpoints configuration"""
    endpoints_data = {
        "openAI": {
            "enabled": True,
            "available": True,
            "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4o"]
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
            "endpoint": "openAI"
        })
    
    return result

@router.post("/ask/openAI")
async def ask_openai(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        data = await request.json()
        
        # Try to get OpenAI-style messages array
        messages = data.get("messages")
        model = data.get("model", "gpt-3.5-turbo")

        # If not present, try to convert from flat format
        if not messages:
            # Check for 'text' and 'sender' fields (LibreChat flat format)
            if "text" in data and "sender" in data:
                messages = [{
                    "role": "user" if data.get("sender", "").lower() == "user" else "assistant",
                    "content": data.get("text", "")
                }]
                model = data.get("model", "gpt-3.5-turbo")
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
        
        # TODO: Replace with actual response from OpenAI when API key is added
        # For now, create a more contextual response using memory
        if context_messages:
            context_summary = f"Context: {len(context_messages)} previous messages in conversation '{conversation_title}'"
        else:
            context_summary = "This is a new conversation"
            
        placeholder_content = f'''API Key is still needed. This is a placeholder response.
                                    {context_summary}
                                    Your message was: "{user_message}"'''
        
        # Get parent message ID from request
        parent_message_id = data.get("parentMessageId", "00000000-0000-0000-0000-000000000000")
        
        # Create message IDs
        user_message_id = str(uuid.uuid4())
        assistant_message_id = response_id
        
        try:
            # Store the user message in the database
            user_msg = Message(
                message_id=user_message_id,
                conversation_id=conversation.id,
                parent_message_id=parent_message_id,
                role="user",
                content=user_message,
                is_created_by_user=True
            )
            db.add(user_msg)
            
            # Store the assistant message in the database
            assistant_msg = Message(
                message_id=assistant_message_id,
                conversation_id=conversation.id,
                parent_message_id=user_message_id,
                role="assistant",
                content=placeholder_content,
                is_created_by_user=False
            )
            db.add(assistant_msg)
            
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Database error: {e}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        # Create the messages that the frontend expects (matching the original format)
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
            "model": None,
            "endpoint": "openAI"
        }
        
        response_message = {
            "messageId": assistant_message_id,
            "conversationId": str(conversation.id),
            "parentMessageId": user_message_id,
            "sender": "GPT-3.5",
            "text": placeholder_content,
            "isCreatedByUser": False,
            "createdAt": assistant_msg.created_at.isoformat(),
            "updatedAt": assistant_msg.created_at.isoformat(),
            "model": model,
            "endpoint": "openAI",
            "unfinished": False,
            "error": False,
            "isEdited": False
        }
        
        # Create the final response data that triggers finalHandler (matching original format)
        final_response_data = {
            "final": True,
            "title": conversation.title,
            "conversation": {
                "conversationId": str(conversation.id),
                "title": conversation.title,
                "user": str(conversation.user_id),
                "createdAt": conversation.created_at.isoformat(),
                "updatedAt": conversation.updated_at.isoformat(),
                "model": model,
                "endpoint": "openAI",
                "isArchived": False,
                "messages": [user_message_id, assistant_message_id]
            },
            "requestMessage": request_message,
            "responseMessage": response_message
        }

        # Return as SSE stream with proper format
        def generate_sse():
            # Add a small delay to simulate processing time
            import time
            time.sleep(0.5)
            
            # Send the final response data as a single SSE event
            yield f"event: message\ndata: {json.dumps(final_response_data)}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate_sse(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
        
    except Exception as e:
        print(f"Error in ask_openai: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 