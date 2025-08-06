TODO: 
- Define Pydantic models for response structure
- Provide factory classes for creating responses
- Write functions for common patters
- Handle errors
- Add global error handlers to catch fastapi's validation errors
- Change frontend to use new response structure since current structure has
  to catch a bunch of different responses including FastAPI's validation errors




TODO:
1. auth.py
    POST /auth/login - Returns old format: {"token": "...", "token_type": "bearer", "user": {...}}
    POST /auth/logout - Returns old format: {"message": "Logout successful"}
    POST /auth/refresh - Returns old format: {"token": "...", "token_type": "bearer", "user": {...}}
2. user.py
    GET /user - Returns old format: user_response.model_dump() (direct user object)
3. endpoints.py
    GET /endpoints - Returns direct dictionary: endpoints_data
    GET /test - Returns direct dictionary: {"message": "Test endpoint works!"}
    GET /messages/{conversation_id} - Returns direct list: result
    POST /ask/openAI - Returns StreamingResponse (SSE format, not ApiResponse)
4. messages.py
    GET /{conversation_id}/messages - Returns MessageListResponse (Pydantic model, not ApiResponse)
    POST /{conversation_id}/messages - Returns MessageResponse (Pydantic model, not ApiResponse)
    GET /messages/{message_id} - Returns MessageResponse (Pydantic model, not ApiResponse)
    PUT /messages/{message_id} - Returns MessageResponse (Pydantic model, not ApiResponse)
    DELETE /messages/{message_id} - Returns direct dictionary or raises HTTPException
5. memory.py
    GET /context/{conversation_id} - Returns direct dictionary with conversation context
    GET /summary/{conversation_id} - Returns direct dictionary with summary
    GET /user/memory - Returns direct dictionary with user memory
    GET /search - Returns direct dictionary with search results
    GET /timeline/{conversation_id} - Returns direct dictionary with timeline
    POST /cleanup - Returns direct dictionary with cleanup results
    GET /stats - Returns direct dictionary with stats
6. models.py
    GET /models - Returns direct dictionary: models_data
