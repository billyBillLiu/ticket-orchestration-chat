# app/services/planner_service.py
from __future__ import annotations
import json
from typing import Dict
from app.services.catalog_service import slice_catalog_for_prompt
from app.models.ticket_agent import TicketPlan, TicketItem
from app.services.llm_service import chat  # <-- your existing Ollama wrapper

# System prompt keeps the model focused on producing a JSON plan only.
SYSTEM_PLAN = """You are a Service Ticket Planner.
Return ONLY JSON. No prose.

Using the allowed catalog (service areas, categories, ticket types), propose 1-3 ticket items
that satisfy the user's request.

CRITICAL RULES:
- Use only the provided categories and ticket types.
- Choose concise, action-oriented titles.
- ONLY prefill fields that are EXPLICITLY provided in the user's text.
- Leave ALL other fields completely empty/blank - do NOT invent or guess values.
- Do NOT use placeholder text like "your_email@example.com" or "[Investor Name]".
- Do NOT use example values like "user@example.com" or "medium" urgency.
- If the user doesn't provide specific values, leave the form completely empty.
- Do NOT invent fields or values outside the catalog.
- The email field will be automatically filled by the system - do NOT prefill it.

EXAMPLE: If user says "Help me create a loan tape ticket", the form should be:
{
  "email": "",
  "summary": "",
  "description": "",
  "urgency": "",
  "request_date": "",
  "vendor_name": "",
  "type_of_rerun": ""
}

NOT:
{
  "email": "user@example.com",
  "summary": "Loan tape verification",
  "description": "Verify loan tape",
  "urgency": "medium",
  "request_date": "2023-03-15",
  "vendor_name": "Pagaya",
  "type_of_rerun": "full"
}
This should be the case for all tickets, not just loan tape tickets.

Output format:
{
  "items": [
    {
      "service_area": "<area key>",
      "category": "<category name>",
      "ticket_type": "<ticket type>",
      "title": "<short actionable title>",
      "description": "<short context>",
      "form": {},      // key:value map for fields
      "labels": []
    }
  ],
  "meta": { "request_text": "<echo of user text>" }
}
"""

def create_mock_plan(user_text: str, user_email: str = None) -> TicketPlan:
    """Create a mock plan for testing when LLM is not available"""
    # Get catalog slice to use real ticket types
    catalog_slice = slice_catalog_for_prompt(user_text)
    
    # Simple keyword-based ticket selection using actual catalog
    user_lower = user_text.lower()
    
    if "datadog" in user_lower and "log" in user_lower:
        # Use actual Datadog log ticket type
        return TicketPlan(
            items=[
                TicketItem(
                    service_area="SRE/Production Support",
                    category="IT Service Requests",
                    ticket_type="Datadog Log Setup/Troubleshooting",
                    title="Datadog Log Assistance",
                    description="Help with Datadog log setup or troubleshooting",
                    form={
                        "email": user_email or "",
                        "summary": "",
                        "scope_of_work": ""
                    },
                    labels=["needs-triage"]
                )
            ],
            meta={"request_text": user_text}
        )
    elif "datadog" in user_lower and "monitor" in user_lower:
        # Use actual Datadog monitor ticket type
        return TicketPlan(
            items=[
                TicketItem(
                    service_area="SRE/Production Support",
                    category="IT Service Requests",
                    ticket_type="Datadog Monitors and Dashboards",
                    title="Datadog Monitor Setup",
                    description="Setup Datadog monitoring and dashboards",
                    form={
                        "email": user_email or "",
                        "summary": "",
                        "service_name": "",
                        "alert_priority": ""
                    },
                    labels=["needs-triage"]
                )
            ],
            meta={"request_text": user_text}
        )
    elif "sftp" in user_lower:
        # Use actual SFTP ticket type
        return TicketPlan(
            items=[
                TicketItem(
                    service_area="SRE/Production Support",
                    category="IT Service Requests",
                    ticket_type="SFTP New Connectivity",
                    title="SFTP Connection Setup",
                    description="Establish SFTP connectivity",
                    form={
                        "email": user_email or "",
                        "summary": "",
                        "investor_name": "",
                        "sftp_server_address": ""
                    },
                    labels=["needs-triage"]
                )
            ],
            meta={"request_text": user_text}
        )
    else:
        # Default to incident report using actual catalog
        return TicketPlan(
            items=[
                TicketItem(
                    service_area="SRE/Production Support",
                    category="Report an Incident",
                    ticket_type="Open an incident here",
                    title="General Support Request",
                    description="Support request",
                    form={
                        "email": user_email or "",
                        "summary": ""
                    },
                    labels=["needs-triage"]
                )
            ],
            meta={"request_text": user_text}
        )

async def plan_from_text_async(user_text: str, user_email: str = None) -> TicketPlan:
    """
    Async version of plan_from_text that works within FastAPI's async context.
    """
    print(f"🔍 PLANNER: Starting async plan_from_text for: '{user_text}'")
    
    cat_slice = slice_catalog_for_prompt(user_text)
    print(f"📋 PLANNER: Catalog slice has {len(cat_slice.get('service_areas', []))} service areas")

    messages = [
        {"role": "system", "content": SYSTEM_PLAN},
        # Put the catalog slice as JSON in the assistant "context" turn,
        # so the model can see the allowed categories/ticket types/fields.
        {"role": "assistant", "content": json.dumps({"catalog": cat_slice})},
        {"role": "user", "content": user_text}
    ]

    print(f"🤖 PLANNER: Calling LLM with {len(messages)} messages")
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
            print(f"✅ PLANNER: Successfully parsed JSON, creating TicketPlan")
            return TicketPlan(**data)
        except json.JSONDecodeError as e:
            print(f"❌ PLANNER: JSON parsing failed: {e}")
            print(f"Raw content: {raw}")
            raise
    except Exception as e:
        # Fallback to mock plan if LLM fails
        print(f"❌ PLANNER: LLM failed, using mock plan: {e}")
        print(f"🔄 PLANNER: Creating mock plan...")
        mock_plan = create_mock_plan(user_text, user_email)
        print(f"✅ PLANNER: Mock plan created with {len(mock_plan.items)} items")
        return mock_plan

def plan_from_text(user_text: str) -> TicketPlan:
    """
    1) Slice the catalog based on the user message (reduce noise).
    2) Ask the LLM to produce a small plan (1-3 items) using that slice.
    3) Parse as JSON and validate against TicketPlan Pydantic model.
    """
    print(f"🔍 PLANNER: Starting plan_from_text for: '{user_text}'")
    
    cat_slice = slice_catalog_for_prompt(user_text)
    print(f"📋 PLANNER: Catalog slice has {len(cat_slice.get('service_areas', []))} service areas")

    messages = [
        {"role": "system", "content": SYSTEM_PLAN},
        # Put the catalog slice as JSON in the assistant "context" turn,
        # so the model can see the allowed categories/ticket types/fields.
        {"role": "assistant", "content": json.dumps({"catalog": cat_slice})},
        {"role": "user", "content": user_text}
    ]

    print(f"🤖 PLANNER: Calling LLM with {len(messages)} messages")
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
        print(f"✅ PLANNER: Successfully parsed JSON, creating TicketPlan")
        return TicketPlan(**data)
    except Exception as e:
        # Fallback to mock plan if LLM fails
        print(f"❌ PLANNER: LLM failed, using mock plan: {e}")
        print(f"🔄 PLANNER: Creating mock plan...")
        mock_plan = create_mock_plan(user_text, user_email)
        print(f"✅ PLANNER: Mock plan created with {len(mock_plan.items)} items")
        return mock_plan
