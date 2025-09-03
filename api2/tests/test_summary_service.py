#!/usr/bin/env python3
"""Test script for the summary service"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.services.summary_service import generate_ticket_summary
from app.models.ticket_agent import TicketItem

async def test_summary_generation():
    """Test the summary generation functionality"""
    print("🧪 Testing summary generation...")
    
    # Create a test ticket item
    test_ticket = TicketItem(
        service_area="SRE/Production Support",
        category="IT Service Requests",
        ticket_type="Datadog Log Setup/Troubleshooting",
        title="Datadog Log Assistance",
        description="Help with Datadog log setup or troubleshooting",
        form={
            "email": "test@example.com",
            "summary": "",  # Empty - should be generated
            "scope_of_work": "Setup logging for payment-service",
            "service_name": "payment-service"
        },
        labels=["needs-triage"]
    )
    
    try:
        summary = await generate_ticket_summary(test_ticket)
        print(f"✅ Generated summary: '{summary}'")
        print(f"📏 Summary length: {len(summary)} characters")
        
        if len(summary) <= 75:
            print("✅ Summary is within character limit")
        else:
            print("❌ Summary exceeds character limit")
            
    except Exception as e:
        print(f"❌ Error generating summary: {e}")
        return False
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_summary_generation())
    if result:
        print("🎉 Summary service test passed!")
    else:
        print("💥 Summary service test failed!")
        sys.exit(1)
