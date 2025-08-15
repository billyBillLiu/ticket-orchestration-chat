#!/usr/bin/env python3
"""
Simple test script without streaming to isolate the issue
"""
import jwt
import requests
import json
from datetime import datetime, timedelta

# Test configuration
BASE_URL = "http://localhost:8000"
SECRET_KEY = "your-secret-key-here"  # Same as in config.py

def create_test_token():
    """Create a valid JWT token for testing"""
    payload = {
        "sub": "2",  # User ID from test user
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def test_chat():
    """Test the chat endpoint"""
    print("Testing chat endpoint without streaming...")
    
    # Create test token
    token = create_test_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test data
    test_data = {
        "messages": [
            {"role": "user", "content": "Hello, how are you?"}
        ],
        "model": "gpt-3.5-turbo",
        "conversationId": None,
        "parentMessageId": None
    }
    
    print(f"Request data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ask/custom",
            headers=headers,
            json=test_data,
            stream=False  # Don't stream
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("Response:")
            print(response.text)
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chat() 