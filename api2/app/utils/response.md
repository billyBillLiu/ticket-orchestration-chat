TODO: 
- Define Pydantic models for response structure
- Provide factory classes for creating responses
- Write functions for common patters
- Handle errors
- Add global error handlers to catch fastapi's validation errors
- Change frontend to use new response structure since current structure has
  to catch a bunch of different responses including FastAPI's validation errors




TODO:
auth.py:
        return Registrat
    POST /auth/register:ionResponse(success=True, message="...", user=db_user)
        return RegistrationResponse(success=False, message="...", error_type="...")

    POST /auth/login
        return {"token": access_token, "token_type": "bearer", "user": user}

    GET /auth/me
        return current_user (uses Pydantic model)

    POST /auth/logout
        return {"message": "Successfully logged out"}

    POST /auth/refresh
        return {"token": access_token, "token_type": "bearer", "user": user}

    POST /auth/verify
        return {"message": "Email verification is disabled. No action taken."}

endpoints.py:
    GET /endpoints
        return {"openAI": {...}, "anthropic": {...}, ...}
    
    GET /test 
        return {"message": "Test endpoint works!"}

    GET /messages/{conversation_id}
        return result (array of message objects)

    POST /ask/openAI
        Streaming response with SSE format

conversations.py:
    GET /convos
        return ConversationListResponse(conversations=..., total=...)

    POST /convos
        return ConversationResponse.model_validate(conversation)

    GET /convos/{conversation_id}
        return ConversationResponse.model_validate(conversation)

    PUT /convos/{conversation_id}
        return ConversationResponse.model_validate(conversation)

    DELETE /convos/{conversation_id}
        return {"message": "Conversation deleted successfully"}

    POST /convos/{conversation_id}/archive
        return ConversationResponse.model_validate(conversation)

    POST /convos/{conversation_id}/unarchive
        return ConversationResponse.model_validate(conversation)

    GET /convos/{conversation_id}/stats
        return stats (dict with conversation statistics)

messages.py:
    GET /convos/{conversation_id}/messages
        return MessageListResponse(messages=..., total=...)

    POST /convos/{conversation_id}/messages
        return MessageResponse.model_validate(new_message)

    GET /convos/messages/{message_id}
        return MessageResponse.model_validate(message)

    PUT /convos/messages/{message_id}
        return MessageResponse.model_validate(updated_message)

    DELETE /convos/messages/{message_id}
        return {"message": "Message deleted successfully"}

user.py:
    GET /user
        return {"id": ..., "username": ..., "email": ..., ...}

config.py:
    GET /config
        return {"appTitle": ..., "appDescription": ..., ...}

files.py:
    GET /files
        return []

    GET /files/speech/config/get
        return {"enabled": False, "provider": "none"}

    GET /files/config
        return {"enabled": True, "maxSize": ..., "allowedTypes": [...]}

stubs.py:
    GET /presets
        return []

    GET /keys
        return {"keys": [], "total": 0}

    GET /agents/tools/web_search/auth
        return {"enabled": False, "authenticated": False}

    GET /agents/tools/execute_code/auth
        return {"enabled": False, "authenticated": False}

    GET /roles/user
        return {"roles": ["user"], "defaultRole": "user"}

    GET /search/enable
        return {"enabled": False, "provider": "none"}

    GET /banner
        return {"enabled": False, "message": "", "type": "info"}

memory.py:
    GET /memory/context/{conversation_id}
        return {"conversation_id": ..., "conversation_title": ..., "messages": ..., ...}

    GET /memory/summary/{conversation_id}
        return summary (dict with conversation summary)

    GET /memory/user/memory
        return memory (dict with user conversation memory)

    GET /memory/search
        return search_results (dict with search results)

    GET /memory/timeline/{conversation_id}
        return timeline (dict with conversation timeline)

    POST /memory/cleanup
        return {"message": "Cleanup completed", "deleted_count": ...}

    GET /memory/stats
        return stats (dict with memory statistics)

models.py:
    GET /models
        return {"openAI": ["gpt-3.5-turbo", "gpt-4", "gpt-4o"]}

main.py:
    GET /health
        return {"status": "healthy", "message": "FastAPI backend is running"}

    GET /api/info
        return {"name": "LibreChat API", "version": "1.0.0", ...}

    GET /{full_path:path}
        return FileResponse or HTMLResponse (frontend serving)
