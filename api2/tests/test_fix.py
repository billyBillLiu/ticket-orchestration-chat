#!/usr/bin/env python3
"""
Test script to verify the fix for the e.some error
"""
import asyncio
import json
import aiohttp
import jwt
from datetime import datetime, timedelta

# Test configuration
BASE_URL = "http://localhost:8000"

# Create a test JWT token
def create_test_token():
    payload = {
        "sub": "1",  # User ID
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    return jwt.encode(payload, "your-secret-key-here", algorithm="HS256")

async def test_chat_fix():
    # Create test token
    token = create_test_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test data with conversation continuation
    test_data = {
        "messages": [
            {"role": "user", "content": "Hello, how are you today?"}
        ],
        "model": "gpt-3.5-turbo",
        "conversationId": None,  # This should create a new conversation
        "parentMessageId": None
    }
    
    print("Testing chat endpoint with fix...")
    print(f"Request data: {json.dumps(test_data, indent=2)}")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BASE_URL}/api/ask/custom",
            headers=headers,
            json=test_data
        ) as response:
            print(f"Status: {response.status}")
            
            if response.status == 200:
                print("Response (SSE stream):")
                async for line in response.content:
                    line_str = line.decode('utf-8').strip()
                    if line_str:
                        print(f"  {line_str}")
                        
                        # Try to parse the data to check format
                        if line_str.startswith("data: "):
                            try:
                                data_str = line_str[6:]  # Remove "data: " prefix
                                if data_str != "[DONE]":
                                    data = json.loads(data_str)
                                    print(f"    Parsed data keys: {list(data.keys())}")
                                    if "requestMessage" in data:
                                        print(f"    Request message keys: {list(data['requestMessage'].keys())}")
                                    if "responseMessage" in data:
                                        print(f"    Response message keys: {list(data['responseMessage'].keys())}")
                            except json.JSONDecodeError:
                                print(f"    Could not parse JSON: {data_str}")
            else:
                error_text = await response.text()
                print(f"Error: {error_text}")

if __name__ == "__main__":
    asyncio.run(test_chat_fix()) 