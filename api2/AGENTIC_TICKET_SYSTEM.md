# Agentic Ticket Creation System

This document describes the comprehensive agentic ticket creation system that follows the **Perceive → Plan → Ask → Fill** loop, with enhanced field validation, type conversion, and user experience.

## Overview

The system allows users to create support tickets through natural language conversation. The agent:

1. **Perceives** the user's request and slices the catalog to relevant ticket types
2. **Plans** which tickets to create based on the request
3. **Asks** follow-up questions to fill required fields
4. **Fills** the ticket with complete information and creates it

The system has been enhanced to provide better field validation, type conversion, and user experience through intelligent input processing and comprehensive error handling.

## Architecture

### Core Components

#### 1. Catalog System (`app/catalog.py`)
- Contains all ticket type definitions with fields, options, and validation rules
- Organized by service areas and categories
- Supports various field types: string, rich_text, bool, int, date, time, file, files, choice, multi_choice

#### 2. Catalog Service (`app/services/catalog_service.py`)
- `slice_catalog_for_prompt()`: Intelligently filters catalog based on user keywords
- `find_ticket_spec()`: Retrieves specific ticket type definitions
- `resolve_field_options()`: Handles choice/multi_choice field options

#### 3. Planner Service (`app/services/planner_service.py`)
- `plan_from_text()`: Uses LLM to generate ticket plans from user requests
- Falls back to mock planning when LLM is unavailable
- Creates structured `TicketPlan` objects with 1-3 ticket items

#### 4. Validator Service (`app/services/validator_service.py`)
- `find_missing_fields()`: Identifies required fields that need values
- `render_question()`: Converts missing fields into user-friendly questions
- `apply_answer()`: Updates ticket plans with user responses

#### 5. Field Processor (`app/services/field_processor.py`)
The field processor handles type conversion and validation for different field types:

- **String/Rich Text**: Passes through as-is
- **Boolean**: Converts "true"/"false", "yes"/"no", "1"/"0" to boolean values
- **Integer**: Extracts numbers from text (e.g., "The code is 42" → 42)
- **Date**: Converts various date formats to ISO format (YYYY-MM-DD) with LLM assistance for natural language
- **Time**: Converts various time formats to HH:MM format
- **Choice**: Matches user input to available options (exact, partial, or LLM-assisted)
- **Multi-Choice**: Handles multiple selections separated by commas, semicolons, or "and"

#### 6. Async Field Processor (`app/services/async_field_processor.py`)
Async version that can use LLM for better choice matching when exact/partial matches fail.

#### 7. Session Management (`app/utils/session_store.py`)
- In-memory session storage for conversation state
- Tracks conversation turns, plans, and pending questions

#### 8. Agent API (`app/routes/agent.py`)
- `/chat/start`: Creates new conversation sessions
- `/chat/{sid}/message`: Main conversation endpoint
- Handles the complete perceive-plan-ask-fill loop

## Data Models

### TicketPlan
```python
class TicketPlan(BaseModel):
    items: List[TicketItem]      # 1-3 planned tickets
    meta: Dict[str, Any]         # Request context
```

### TicketItem
```python
class TicketItem(BaseModel):
    service_area: str            # e.g., "SRE/Production Support"
    category: str                # e.g., "IT Service Requests"
    ticket_type: str             # e.g., "Datadog Monitors and Dashboards"
    title: str                   # Short, actionable title
    description: str             # Context for executor
    form: Dict[str, Any]         # Field values collected
    labels: List[str]            # e.g., ["needs-triage"]
```

### ConversationState
```python
class ConversationState(BaseModel):
    session_id: str
    turns: List[ChatTurn]        # Conversation history
    plan: Optional[TicketPlan]   # Current ticket plan
    pending: List[MissingField]  # Fields awaiting answers
    completed: bool              # Whether tickets are ready
```

## Field Types and Processing

### Supported Field Types

- **string**: Simple text input
- **rich_text**: Formatted text with file attachments
- **bool**: True/false checkbox
- **int**: Numeric input
- **date**: Date picker
- **time**: Time picker
- **file**: Single file upload
- **files**: Multiple file uploads
- **choice**: Single selection dropdown
- **multi_choice**: Multiple selection checkboxes

### Field Processing Examples

#### Integer Field
**User Input**: "The error code is 404"
**Field Type**: int
**Result**: 404

#### Date Field
**User Input**: "January 15, 2024"
**Field Type**: date
**Result**: "2024-01-15"

**User Input**: "tomorrow"
**Field Type**: date
**Result**: "2024-01-16" (or current date + 1 day)

**User Input**: "next Monday"
**Field Type**: date
**Result**: "2024-01-22" (or next Monday's date)

#### Choice Field
**User Input**: "high priority"
**Field Type**: choice
**Options**: ["critical", "high", "medium", "low"]
**Result**: "high"

#### Multi-Choice Field
**User Input**: "critical and high"
**Field Type**: multi_choice
**Options**: ["critical", "high", "medium", "low"]
**Result**: ["critical", "high"]

### Enhanced Question Rendering

The `render_question` function now includes available options in the question text for choice fields:

```
Select **urgency**.

Available options:
• critical
• high
• medium
• low
```

## API Endpoints

### Start Session
```http
POST /agents/chat/start
Response: {"session_id": "uuid"}
```

### Send Message
```http
POST /agents/chat/{session_id}/message
Body: {
  "text": "I need help with datadog monitoring",
  "answer_to": null,  // or {"item_index": 0, "field_name": "email"}
  "context": {}       // optional metadata
}
```

### Response Types

#### Need More Information
```json
{
  "session_id": "uuid",
  "status": "need_more_info",
  "question": {
    "text": "Please provide **email**.",
    "type": "string",
    "options": null,
    "item_index": 0,
    "field_name": "email",
    "description": ""
  },
  "plan_preview": {...}
}
```

#### Complete
```json
{
  "session_id": "uuid",
  "status": "done",
  "result": {
    "created": [
      {
        "pseudo_id": "SRE-1001",
        "service_area": "SRE/Production Support",
        "category": "IT Service Requests",
        "ticket_type": "Datadog Monitors and Dashboards",
        "title": "Setup Datadog Monitor",
        "form": {...}
      }
    ]
  },
  "plan": {...}
}
```

## Usage Flow

1. **User starts conversation**: "I need help with datadog monitoring"
2. **System perceives**: Slices catalog to IT Service Requests
3. **System plans**: Creates Datadog Monitors and Dashboards ticket
4. **System asks**: "Please provide **email**."
5. **User answers**: "john@example.com"
6. **System asks**: "Please provide **summary**."
7. **User answers**: "Setup monitoring for my service"
8. **System completes**: Creates ticket and returns summary

## Configuration

The system uses the existing LLM service configuration:
- Supports Ollama and OpenAI providers
- Falls back to mock planning when LLM unavailable
- Configurable temperature, max tokens, etc.

### Planner Mode Configuration

Set the `PLANNER_MODE` environment variable to control planning behavior:

- **`PLANNER_MODE=mock`**: Always use mock planning (fast, no LLM required)
- **`PLANNER_MODE=llm`**: Always use LLM planning (requires Ollama/OpenAI)
- **`PLANNER_MODE=auto`**: Use LLM with fallback to mock (default)

```bash
# Development/testing - fast, no LLM needed
export PLANNER_MODE=mock

# Production - always use LLM
export PLANNER_MODE=llm

# Production with fallback - best of both worlds
export PLANNER_MODE=auto
```

## Error Handling

The system provides clear error messages when processing fails:

- **Invalid boolean**: "Invalid boolean value: 'maybe'. Please use 'true'/'false', 'yes'/'no', or '1'/'0'"
- **Invalid choice**: "Invalid choice: 'invalid'. Available options: critical, high, medium, low"
- **Invalid date**: "Could not parse date from: 'invalid date'. Please use format YYYY-MM-DD, MM/DD/YYYY, or similar."

## Testing

The system includes comprehensive testing:
- Catalog slicing with keyword matching
- Mock planning for development
- Field validation and question generation
- Complete conversation flow simulation

Run the test scripts to verify field processing:

```bash
cd api2
python tests/simple_field_test.py
python tests/test_llm_date_parsing.py
```

## Integration

The agent routes are registered at `/agents/` prefix and can be integrated with:
- Frontend chat interfaces
- Slack/Discord bots
- Email ticket systems
- JIRA/ServiceNow connectors (future)

## Future Enhancements

1. **JIRA Integration**: Connect to actual JIRA for ticket creation
2. **Smart Catalog Slicing**: Use LLM for better catalog filtering
3. **Multi-language Support**: Internationalize field descriptions
4. **Template System**: Pre-defined ticket templates
5. **Approval Workflows**: Add approval steps for certain ticket types
6. **Analytics**: Track ticket creation patterns and success rates
7. **LLM Integration**: Enable LLM-assisted choice matching in the synchronous processor
8. **File Upload**: Implement proper file upload handling
9. **Validation Rules**: Add custom validation rules for specific fields
10. **User Feedback**: Provide suggestions when input doesn't match expected format
