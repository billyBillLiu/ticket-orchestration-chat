#!/usr/bin/env python3
"""
Test script to verify the improved placeholder response
"""
import asyncio
import json
import aiohttp
import jwt
from datetime import datetime, timedelta

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

# Create a test JWT token (you'll need to register a user first)
def create_test_token():
    # This is a simple test token - in production you'd get this from login
    payload = {
        "sub": "1",  # User ID
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    # Use the same secret key as in your config
    return jwt.encode(payload, "your-secret-key-here", algorithm="HS256")

async def test_chat():
    # Create test token
    token = create_test_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test data
    test_data = {
        "messages": [
            {"role": "user", "content": "Hello, how are you today?"}
        ],
        "model": "gpt-3.5-turbo"
    }
    
    print("Testing chat endpoint...")
    print(f"Request data: {json.dumps(test_data, indent=2)}")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BASE_URL}/api/ask/custom",
            headers=headers,
            json=test_data
        ) as response:
            print(f"Status: {response.status}")
            print(f"Headers: {dict(response.headers)}")
            
            if response.status == 200:
                print("Response (SSE stream):")
                async for line in response.content:
                    line_str = line.decode('utf-8').strip()
                    if line_str:
                        print(f"  {line_str}")
            else:
                error_text = await response.text()
                print(f"Error: {error_text}")

if __name__ == "__main__":
    asyncio.run(test_chat()) 