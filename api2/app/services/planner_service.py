# app/services/planner_service.py
from __future__ import annotations
import json
from typing import Dict
from app.services.catalog_service import slice_catalog_for_prompt
from app.models.ticket_agent import TicketPlan
from app.services.llm_service import chat  # <-- existing Ollama wrapper

# System prompt keeps the model focused on ticket identification only.
SYSTEM_PLAN = """
You are a Service Ticket Identifier.
Return ONLY JSON. No prose.

Using the allowed catalog (departments, categories, ticket types), identify 1-3 ticket items
that satisfy the user's request.

CRITICAL RULES:
- Use only the provided categories and ticket types from the catalog.
- Choose concise, action-oriented titles.
- Do NOT attempt to fill any form fields - leave the form completely empty.
- Do NOT invent ticket types - use ONLY the exact ticket_type names from the catalog.
- Focus ONLY on identifying the correct ticket types and categories.
- Field prefilling will be handled by a separate specialized process.
- Return ONLY valid JSON - NO comments, NO trailing commas, NO extra text.
- IMPORTANT: Return a SINGLE JSON object with an array of tickets, not multiple separate JSON objects.

This is the only output format you are allowed to return:
{
  "items": [
    {
      "service_area": "<area key>",
      "category": "<category name>",
      "ticket_type": "<ticket type>",
      "title": "<short actionable title>",
      "description": "<short context>",
      "form": {},
      "labels": []
    }
  ],
  "meta": { "request_text": "<echo of user text>" }
}

EXAMPLES:
- User says "I need a final loan tape for AAA" → ticket_type: "Loan Tape" (form stays empty)
- User says "investor report rerun from july 18 to tomorrow" → ticket_type: "Investor Reports Manual Rerun" (form stays empty)
- User says "high urgency datadog monitoring" → ticket_type: "Datadog Monitors and Dashboards" (form stays empty)
- User says "I need to make a loan tape ticket and a manual loan verification ticket" → returns ONE JSON with TWO items in the items array
"""



async def plan_from_text_async(user_text: str, user_email: str = None) -> TicketPlan:
    """
    Async version of plan_from_text that works within FastAPI's async context.
    Uses a two-step process: 1) Identify tickets, 2) Prefill fields.
    """
    print(f"🔍 PLANNER: Starting async plan_from_text for: '{user_text}'")
    
    # STEP 1: Identify tickets (without field prefilling)
    print(f"📋 PLANNER: Step 1 - Identifying ticket types...")
    
    cat_slice = slice_catalog_for_prompt(user_text)
    print(f"📋 PLANNER: Catalog slice has {len(cat_slice.get('service_areas', []))} service areas")

    # Add user email context if available (for reference only - field prefilling happens separately)
    user_context = ""
    if user_email:
        user_context = f"\n\nUSER EMAIL: {user_email}"

    messages = [
        {"role": "system", "content": SYSTEM_PLAN + user_context},
        # Put the catalog slice as JSON in the assistant "context" turn,
        # so the model can see the allowed categories/ticket types/fields.
        {"role": "assistant", "content": json.dumps({"catalog": cat_slice})},
        {"role": "user", "content": user_text}
    ]

    print(f"🤖 PLANNER: Calling LLM for ticket identification with {len(messages)} messages")
    try:
        # Use the LLM service directly instead of the chat function
        from app.services.llm_service import llm_service, Message as LLMMessage
        
        # Convert messages to Message objects
        message_objects = [LLMMessage(**msg) for msg in messages]
        
        # Call LLM directly - don't use context manager to keep client open
        response = await llm_service.generate_non_streaming_response(
            messages=message_objects,
            model="llama3:8b",  # Use the actual model name
            temperature=0.2,
            max_tokens=4096
        )
        
        raw = response.content
        print(f"📥 PLANNER: LLM returned raw response: '{raw[:100]}...'")
        
        # Clean up the response - remove markdown formatting and extra text
        print(f"🔧 PLANNER: Cleaning up LLM response...")
        
        # Look for JSON code blocks
        if "```json" in raw:
            # Extract JSON from markdown code block
            start = raw.find("```json") + 7
            end = raw.find("```", start)
            if end != -1:
                raw = raw[start:end].strip()
                print(f"🔧 PLANNER: Extracted JSON from code block")
        elif "```" in raw:
            # Extract JSON from regular code block
            start = raw.find("```") + 3
            end = raw.find("```", start)
            if end != -1:
                raw = raw[start:end].strip()
                print(f"🔧 PLANNER: Extracted JSON from regular code block")
        
        # Try to find JSON object boundaries if still not clean
        if not raw.strip().startswith("{"):
            # Look for the first { and last }
            start_brace = raw.find("{")
            end_brace = raw.rfind("}")
            if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
                raw = raw[start_brace:end_brace + 1]
                print(f"🔧 PLANNER: Extracted JSON object from text")
        
        print(f"🔧 PLANNER: Cleaned content: {raw[:100]}...")
        
        # Try to parse the JSON
        try:
            data = json.loads(raw)
            print(f"✅ PLANNER: Successfully parsed JSON, creating initial TicketPlan")
            initial_plan = TicketPlan(**data)
            
            # STEP 2: Prefill fields using specialized field prefiller
            print(f"🔧 PLANNER: Step 2 - Prefilling fields using specialized service...")
            from app.services.field_prefiller_service import prefill_plan_fields_async
            
            final_plan = await prefill_plan_fields_async(initial_plan, user_text, user_email)
            print(f"✅ PLANNER: Completed two-step process - tickets identified and fields prefilled")
            
            return final_plan
            
        except json.JSONDecodeError as e:
            print(f"❌ PLANNER: JSON parsing failed: {e}")
            print(f"Raw content: {raw}")
            raise
    except Exception as e:
        # Re-raise the exception if LLM fails
        print(f"❌ PLANNER: LLM failed: {e}")
        raise

def plan_from_text(user_text: str, user_email: str = None) -> TicketPlan:
    """
    1) Slice the catalog based on the user message (reduce noise).
    2) Ask the LLM to identify ticket types (without field prefilling).
    3) Use specialized field prefiller to fill fields with full context.
    4) Parse as JSON and validate against TicketPlan Pydantic model.
    """
    print(f"🔍 PLANNER: Starting plan_from_text for: '{user_text}'")
    
    # STEP 1: Identify tickets (without field prefilling)
    print(f"📋 PLANNER: Step 1 - Identifying ticket types...")
    
    cat_slice = slice_catalog_for_prompt(user_text)
    print(f"📋 PLANNER: Catalog slice has {len(cat_slice.get('service_areas', []))} service areas")

    # Add user email context if available (for reference only - field prefilling happens separately)
    user_context = ""
    if user_email:
        user_context = f"\n\nUSER EMAIL: {user_email}"

    messages = [
        {"role": "system", "content": SYSTEM_PLAN + user_context},
        # Put the catalog slice as JSON in the assistant "context" turn,
        # so the model can see the allowed categories/ticket types/fields.
        {"role": "assistant", "content": json.dumps({"catalog": cat_slice})},
        {"role": "user", "content": user_text}
    ]

    print(f"🤖 PLANNER: Calling LLM for ticket identification with {len(messages)} messages")
    try:
        # Important: enforce JSON-only output from the model
        raw = chat(
            messages,
            model="llama3.1:8b",   # substitute your local model
            format="json",
            options={"temperature": 0.2, "top_p": 0.9, "num_ctx": 4096},
        )

        print(f"📥 PLANNER: LLM returned raw response: '{raw[:100]}...'")
        
        data = json.loads(raw)
        print(f"✅ PLANNER: Successfully parsed JSON, creating initial TicketPlan")
        initial_plan = TicketPlan(**data)
        
        # STEP 2: Prefill fields using specialized field prefiller
        print(f"🔧 PLANNER: Step 2 - Prefilling fields using specialized service...")
        # Note: For synchronous version, we'll use a simple approach without async field prefilling
        # In a real implementation, you might want to make this async or use a different approach
        
        # For now, return the initial plan (fields will be filled during the conversation flow)
        print(f"✅ PLANNER: Completed ticket identification step")
        return initial_plan
        
    except Exception as e:
        # Re-raise the exception if LLM fails
        print(f"❌ PLANNER: LLM failed: {e}")
        raise
