#!/usr/bin/env python3
"""
Test chat endpoint with real token from login
"""
import requests
import json

def test_chat_with_real_token():
    """Test chat endpoint with real token"""
    print("Testing chat endpoint with real token...")
    
    try:
        # First, get a real token by logging in
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        login_response = requests.post(
            "http://localhost:8000/api/auth/login",
            json=login_data
        )
        
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.text}")
            return
        
        token_data = login_response.json()
        token = token_data.get("access_token")
        print(f"Got token: {token[:50]}...")
        
        # Now test the chat endpoint with the real token
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        chat_data = {
            "messages": [
                {"role": "user", "content": "Hello, how are you?"}
            ],
            "model": "gpt-3.5-turbo",
            "conversationId": None,
            "parentMessageId": None
        }
        
        print(f"Chat request data: {json.dumps(chat_data, indent=2)}")
        
        chat_response = requests.post(
            "http://localhost:8000/api/ask/custom",
            headers=headers,
            json=chat_data,
            stream=False
        )
        
        print(f"Chat status: {chat_response.status_code}")
        print(f"Chat headers: {dict(chat_response.headers)}")
        
        if chat_response.status_code == 200:
            print("Chat response:")
            print(chat_response.text)
        else:
            print(f"Chat error: {chat_response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_chat_with_real_token() 