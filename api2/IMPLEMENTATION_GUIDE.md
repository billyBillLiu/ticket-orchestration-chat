# Standardized Response Implementation Guide

## Overview

This guide explains how to implement standardized responses across all endpoints in the API. The new system provides consistent response structures for success, error, and validation cases.

## Response Structure

### Base Response Fields
All responses now include:
- `success`: Boolean indicating if the request was successful
- `message`: Human-readable message
- `timestamp`: ISO 8601 timestamp of the response

### Success Response
```json
{
  "success": true,
  "data": {...},
  "message": "Success",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error message",
  "error_type": "ERROR_TYPE",
  "error_code": 400,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Validation Error Response
```json
{
  "success": false,
  "message": "Validation failed",
  "error_type": "VALIDATION_ERROR",
  "error_code": 422,
  "details": {
    "validation_errors": [
      {
        "field": "email",
        "message": "value is not a valid email address",
        "value": "invalid-email"
      }
    ]
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Implementation Steps

### 1. Import Response Utilities

Add to the top of each route file:
```python
from app.utils.response_utils import (
    create_success_response,
    create_error_response,
    SuccessResponse,
    ErrorResponse
)
```

### 2. Replace Direct Returns

**Before:**
```python
@router.get("/endpoint")
async def get_data():
    return {"data": "value"}
```

**After:**
```python
@router.get("/endpoint")
async def get_data():
    return create_success_response({"data": "value"}, "Data retrieved successfully")
```

### 3. Handle Errors Consistently

**Before:**
```python
if not user:
    raise HTTPException(status_code=404, detail="User not found")
```

**After:**
```python
if not user:
    return create_error_response("User not found", "USER_NOT_FOUND", 404)
```

## Endpoint-Specific Guidelines

### Authentication Endpoints (`auth.py`)

✅ **COMPLETED**: `/auth/register` - Uses `RegistrationSuccessResponse` and `RegistrationErrorResponse`

**Remaining endpoints:**
- `/auth/login`: Return `UserLoginResponse` (keep existing structure)
- `/auth/me`: Return `UserResponse` (keep existing structure)
- `/auth/logout`: Use `create_success_response`
- `/auth/refresh`: Return `UserLoginResponse` (keep existing structure)
- `/auth/verify`: Use `create_success_response`

### Configuration Endpoints (`config.py`)

- `/config`: Use `create_success_response` with config data
- All config endpoints: Use `create_success_response`

### Endpoint Lists (`endpoints.py`)

- `/endpoints`: Use `create_success_response` with endpoint data
- `/test`: Use `create_success_response`
- `/messages/{conversation_id}`: Use `create_success_response` with message array

### Conversations (`conversations.py`)

- `/convos`: Use `create_paginated_response` for conversation list
- `/convos` (POST): Use `create_success_response` with conversation data
- `/convos/{conversation_id}`: Use `create_success_response` with conversation data
- `/convos/{conversation_id}` (PUT): Use `create_success_response` with updated conversation
- `/convos/{conversation_id}` (DELETE): Use `create_success_response` with deletion message
- `/convos/{conversation_id}/archive`: Use `create_success_response` with archived conversation
- `/convos/{conversation_id}/unarchive`: Use `create_success_response` with unarchived conversation
- `/convos/{conversation_id}/stats`: Use `create_success_response` with stats data

### Messages (`messages.py`)

- `/convos/{conversation_id}/messages`: Use `create_paginated_response` for message list
- `/convos/{conversation_id}/messages` (POST): Use `create_success_response` with new message
- `/convos/messages/{message_id}`: Use `create_success_response` with message data
- `/convos/messages/{message_id}` (PUT): Use `create_success_response` with updated message
- `/convos/messages/{message_id}` (DELETE): Use `create_success_response` with deletion message

### User (`user.py`)

- `/user`: Use `create_success_response` with user data

### Files (`files.py`)

- `/files`: Use `create_success_response` with file list
- `/files/speech/config/get`: Use `create_success_response` with config data
- `/files/config`: Use `create_success_response` with config data

### Stubs (`stubs.py`)

- `/presets`: Use `create_success_response` with preset list
- `/keys`: Use `create_success_response` with keys data
- `/agents/tools/web_search/auth`: Use `create_success_response` with auth data
- `/agents/tools/execute_code/auth`: Use `create_success_response` with auth data
- `/roles/user`: Use `create_success_response` with roles data
- `/search/enable`: Use `create_success_response` with search config
- `/banner`: Use `create_success_response` with banner data

### Memory (`memory.py`)

- `/memory/context/{conversation_id}`: Use `create_success_response` with context data
- `/memory/summary/{conversation_id}`: Use `create_success_response` with summary data
- `/memory/user/memory`: Use `create_success_response` with memory data
- `/memory/search`: Use `create_success_response` with search results
- `/memory/timeline/{conversation_id}`: Use `create_success_response` with timeline data
- `/memory/cleanup`: Use `create_success_response` with cleanup results
- `/memory/stats`: Use `create_success_response` with stats data

### Models (`models.py`)

- `/models`: Use `create_success_response` with models data

### Main (`main.py`)

- `/health`: Use `create_success_response` with health data
- `/api/info`: Use `create_success_response` with API info

## Error Handling Patterns

### 1. Not Found Errors
```python
if not resource:
    return create_error_response("Resource not found", "NOT_FOUND", 404)
```

### 2. Permission Errors
```python
if not user.has_permission(action):
    return create_error_response("Insufficient permissions", "PERMISSION_DENIED", 403)
```

### 3. Validation Errors
Automatically handled by global exception handler - no code changes needed.

### 4. Database Errors
```python
try:
    db.commit()
except Exception as e:
    db.rollback()
    return create_error_response("Database operation failed", "DATABASE_ERROR", 500)
```

## Migration Checklist

For each endpoint:

- [ ] Import response utilities
- [ ] Replace direct returns with `create_success_response`
- [ ] Replace `HTTPException` with `create_error_response`
- [ ] Test success case
- [ ] Test error cases
- [ ] Test validation errors (automatic)
- [ ] Update frontend to handle new response structure

## Frontend Integration

The frontend will need to be updated to handle the new response structure:

```javascript
// Before
const response = await fetch('/api/endpoint');
const data = await response.json();

// After
const response = await fetch('/api/endpoint');
const result = await response.json();

if (result.success) {
  // Handle success case
  const data = result.data;
} else {
  // Handle error case
  const error = result.message;
  const errorType = result.error_type;
}
```

## Testing

Use the provided test script to verify responses:
```bash
python test_standardized_responses.py
```

## Benefits

1. **Consistency**: All endpoints return the same response structure
2. **Error Handling**: Centralized error handling with detailed error types
3. **Validation**: Automatic validation error formatting
4. **Frontend Integration**: Easier frontend integration with predictable responses
5. **Debugging**: Better error messages and structured logging 