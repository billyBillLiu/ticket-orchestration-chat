# DELETE Conversations API Documentation

This document describes the DELETE conversation endpoints available in the Ticket Orchestration Chat API.

## Base URL
All endpoints are prefixed with `/api/convos`

## Authentication
All endpoints require authentication. Include your authentication token in the request headers.

## Endpoints

### 1. Delete Specific Conversation
**DELETE** `/api/convos/`

Delete a specific conversation by its ID.

#### Query Parameters
- `conversationId` (string, required): The ID of the conversation to delete

#### Example Request
```bash
curl -X DELETE "http://localhost:3080/api/convos/?conversationId=123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Example Response
```json
{
  "success": true,
  "data": {
    "message": "Successfully deleted 1 conversation(s)",
    "deleted_count": 1
  },
  "message": "Successfully deleted 1 conversation(s)"
}
```

### 2. Delete Conversations by Thread ID
**DELETE** `/api/convos/`

Delete all conversations that contain messages with a specific thread_id.

#### Query Parameters
- `thread_id` (string, required): The thread_id to match

#### Example Request
```bash
curl -X DELETE "http://localhost:3080/api/convos/?thread_id=thread_abc123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Example Response
```json
{
  "success": true,
  "data": {
    "message": "Successfully deleted 2 conversation(s)",
    "deleted_count": 2
  },
  "message": "Successfully deleted 2 conversation(s)"
}
```

### 3. Delete Conversations by Endpoint
**DELETE** `/api/convos/`

Delete all conversations that contain messages from a specific endpoint.

#### Query Parameters
- `endpoint` (string, required): The endpoint to match (e.g., "openai", "anthropic")

#### Example Request
```bash
curl -X DELETE "http://localhost:3080/api/convos/?endpoint=openai" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Example Response
```json
{
  "success": true,
  "data": {
    "message": "Successfully deleted 5 conversation(s)",
    "deleted_count": 5
  },
  "message": "Successfully deleted 5 conversation(s)"
}
```

### 4. Delete All Conversations
**DELETE** `/api/convos/all`

Delete all conversations for the current user.

#### Example Request
```bash
curl -X DELETE "http://localhost:3080/api/convos/all" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Example Response
```json
{
  "success": true,
  "data": {
    "message": "All conversations deleted successfully",
    "deleted_count": 10
  },
  "message": "Successfully deleted 10 conversations"
}
```

## Error Responses

### 400 Bad Request
When no parameters are provided:
```json
{
  "success": false,
  "error": "No parameters provided. Please specify conversationId, thread_id, or endpoint.",
  "status_code": 400
}
```

When invalid conversation ID format is provided:
```json
{
  "success": false,
  "error": "Invalid conversation ID format",
  "status_code": 400
}
```

### 401 Unauthorized
When authentication is missing or invalid:
```json
{
  "success": false,
  "error": "Not authenticated",
  "status_code": 401
}
```

### 403 Forbidden
When user doesn't own the conversation:
```json
{
  "success": false,
  "error": "Access denied",
  "status_code": 403
}
```

### 404 Not Found
When conversation doesn't exist:
```json
{
  "success": false,
  "error": "Conversation not found",
  "status_code": 404
}
```

### 500 Internal Server Error
When an unexpected error occurs:
```json
{
  "success": false,
  "error": "Error deleting conversations: [error details]",
  "status_code": 500
}
```

## Security Features

1. **User Ownership Verification**: All deletion operations verify that the user owns the conversations being deleted
2. **Parameter Validation**: Endpoints validate input parameters to prevent malicious requests
3. **Cascading Deletion**: When a conversation is deleted, all associated messages are also deleted
4. **Bulk Operation Safety**: Bulk deletion operations are protected against accidental deletion of all conversations

## Implementation Details

### Service Layer Methods

The following methods are available in the `ConversationService`:

- `delete_conversation(conversation_id: int, user_id: int) -> bool`: Delete a single conversation
- `delete_all_user_conversations(user_id: int) -> int`: Delete all conversations for a user
- `delete_conversations_by_thread_id(thread_id: str, user_id: int) -> int`: Delete conversations by thread_id
- `delete_conversations_by_endpoint(endpoint: str, user_id: int) -> int`: Delete conversations by endpoint

### Database Operations

1. **Message Deletion**: All messages associated with conversations are deleted first
2. **Conversation Deletion**: Conversations are deleted after their messages
3. **Transaction Safety**: All operations are wrapped in database transactions
4. **User Verification**: Each operation verifies user ownership before deletion

## Testing

You can test the endpoints using the provided test script:

```bash
cd api2
python test_delete_conversations.py
```

Make sure the API server is running on `http://localhost:3080` before running the tests.

## Frontend Integration

The frontend can use these endpoints through the existing data provider:

```typescript
// Delete specific conversation
const deleteMutation = useDeleteConversationMutation();
deleteMutation.mutate({ conversationId: "123", source: "button" });

// Delete all conversations
const clearAllMutation = useClearAllConversationsMutation();
clearAllMutation.mutate();
```

## Notes

- All deletion operations are irreversible
- Deleted conversations and messages cannot be recovered
- The API returns the count of deleted conversations for confirmation
- Bulk operations are optimized for performance using database-level operations
