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

Rules:
- Use only the provided categories and ticket types.
- Choose concise, action-oriented titles.
- Prefill obvious fields from the user text; leave uncertain ones blank.
- If anything is uncertain, add label "needs-triage".
- Do NOT invent fields or values outside the catalog.

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

def create_mock_plan(user_text: str) -> TicketPlan:
    """Create a mock plan for testing when LLM is not available"""
    # Simple keyword-based ticket selection
    user_lower = user_text.lower()
    
    if "datadog" in user_lower and "monitor" in user_lower:
        return TicketPlan(
            items=[
                TicketItem(
                    service_area="SRE/Production Support",
                    category="IT Service Requests",
                    ticket_type="Datadog Monitors and Dashboards",
                    title="Setup Datadog Monitor",
                    description="Create monitoring for service",
                    form={
                        "email": "user@example.com",
                        "summary": "Datadog monitor setup",
                        "service_name": "my-service"
                    },
                    labels=[]
                )
            ],
            meta={"request_text": user_text}
        )
    elif "sftp" in user_lower:
        return TicketPlan(
            items=[
                TicketItem(
                    service_area="SRE/Production Support",
                    category="IT Service Requests",
                    ticket_type="SFTP New Connectivity",
                    title="Setup SFTP Connection",
                    description="Establish SFTP connectivity",
                    form={
                        "email": "user@example.com",
                        "summary": "SFTP connection setup"
                    },
                    labels=[]
                )
            ],
            meta={"request_text": user_text}
        )
    else:
        # Default to incident report
        return TicketPlan(
            items=[
                TicketItem(
                    service_area="SRE/Production Support",
                    category="Report an Incident",
                    ticket_type="Open an incident here",
                    title="General Support Request",
                    description="Support request",
                    form={
                        "email": "user@example.com",
                        "summary": "Support request"
                    },
                    labels=["needs-triage"]
                )
            ],
            meta={"request_text": user_text}
        )

def plan_from_text(user_text: str) -> TicketPlan:
    """
    1) Slice the catalog based on the user message (reduce noise).
    2) Ask the LLM to produce a small plan (1-3 items) using that slice.
    3) Parse as JSON and validate against TicketPlan Pydantic model.
    """
    cat_slice = slice_catalog_for_prompt(user_text)

    messages = [
        {"role": "system", "content": SYSTEM_PLAN},
        # Put the catalog slice as JSON in the assistant "context" turn,
        # so the model can see the allowed categories/ticket types/fields.
        {"role": "assistant", "content": json.dumps({"catalog": cat_slice})},
        {"role": "user", "content": user_text}
    ]

    try:
        # Important: enforce JSON-only output from the model
        raw = chat(
            messages,
            model="llama3.1:8b",   # substitute your local model
            format="json",
            options={"temperature": 0.2, "top_p": 0.9, "num_ctx": 4096},
        )

        data = json.loads(raw)
        return TicketPlan(**data)
    except Exception as e:
        # Fallback to mock plan if LLM fails
        print(f"LLM failed, using mock plan: {e}")
        return create_mock_plan(user_text)
