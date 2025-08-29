# app/services/summary_service.py
from __future__ import annotations
import json
from typing import Dict, Any
from app.models.ticket_agent import TicketPlan, TicketItem
from app.services.llm_service import llm_service, Message as LLMMessage

SYSTEM_SUMMARY = """You are a Ticket Summary Generator.
Generate a concise, descriptive summary (max 75 characters) for a support ticket based on the ticket type and filled form data.

CRITICAL RULES:
- Keep summary under 75 characters
- Be specific and actionable
- Use the ticket type and key form fields to create a meaningful summary
- Focus on the main issue or request
- Use clear, professional language
- Avoid generic terms like "issue" or "problem" unless specific

Examples:
- "Datadog log setup for payment-service"
- "SFTP connection for Pagaya investor"
- "Loan tape rerun for Q1 2024"
- "Monitor alert for high CPU usage"
- "Dashboard creation for risk metrics"

Return ONLY the summary text, no JSON or other formatting."""

async def generate_ticket_summary(ticket_item: TicketItem) -> str:
    """
    Generate a summary for a ticket based on its type and filled form data.
    """
    print(f"📝 SUMMARY: Generating summary for {ticket_item.ticket_type}")
    
    # Build context from ticket data
    context_parts = []
    context_parts.append(f"Ticket Type: {ticket_item.ticket_type}")
    
    # Add relevant form fields to context
    if ticket_item.form:
        for field_name, value in ticket_item.form.items():
            if value and field_name not in ["email", "summary"]:  # Skip email and summary itself
                context_parts.append(f"{field_name}: {value}")
    
    context = "\n".join(context_parts)
    
    messages = [
        {"role": "system", "content": SYSTEM_SUMMARY},
        {"role": "user", "content": f"Generate a summary for this ticket:\n\n{context}"}
    ]
    
    try:
        # Convert messages to Message objects
        message_objects = [LLMMessage(**msg) for msg in messages]
        
        # Call LLM to generate summary
        response = await llm_service.generate_non_streaming_response(
            messages=message_objects,
            model="llama3:8b",
            temperature=0.3,
            max_tokens=100
        )
        
        summary = response.content.strip()
        
        # Ensure summary is within character limit
        if len(summary) > 75:
            summary = summary[:72] + "..."
        
        print(f"✅ SUMMARY: Generated summary: '{summary}'")
        return summary
        
    except Exception as e:
        print(f"❌ SUMMARY: Failed to generate summary: {e}")
        # Fallback to a basic summary
        fallback = f"{ticket_item.ticket_type} request"
        if len(fallback) > 75:
            fallback = fallback[:72] + "..."
        return fallback

async def generate_summaries_for_plan(plan: TicketPlan) -> TicketPlan:
    """
    Generate summaries for all tickets in a plan after all other fields are filled.
    """
    print(f"📝 SUMMARY: Generating summaries for {len(plan.items)} tickets")
    
    for i, item in enumerate(plan.items):
        if not item.form.get("summary"):  # Only generate if summary is empty
            summary = await generate_ticket_summary(item)
            plan.items[i].form["summary"] = summary
    
    return plan
