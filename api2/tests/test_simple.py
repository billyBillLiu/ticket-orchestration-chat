#!/usr/bin/env python3
"""
Simple test script to verify the chat endpoint works
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
    print("Testing chat endpoint...")
    
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
            stream=True
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("Response:")
            for line in response.iter_lines():
                if line:
                    print(f"  {line.decode()}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_chat() 