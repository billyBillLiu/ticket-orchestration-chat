#!/usr/bin/env python3
"""
Simple test to check the endpoint
"""
import requests
import json

def test_endpoint():
    """Test the endpoint directly"""
    print("Testing endpoint directly...")
    
    # Test data
    test_data = {
        "messages": [
            {"role": "user", "content": "Hello"}
        ],
        "model": "gpt-3.5-turbo"
    }
    
    # Test without authentication first
    try:
        response = requests.post(
            "http://localhost:8000/api/ask/openAI",
            json=test_data
        )
        print(f"Status without auth: {response.status_code}")
        print(f"Response without auth: {response.text}")
    except Exception as e:
        print(f"Error without auth: {e}")
    
    # Test with authentication
    try:
        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwiZXhwIjoxNzUzMzg5MzQzfQ.SZ72cUqAF2g-b9sZGwmPoc3HN8Ut4nUB_3cjsRQBv0Q",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "http://localhost:8000/api/ask/openAI",
            headers=headers,
            json=test_data
        )
        print(f"Status with auth: {response.status_code}")
        print(f"Response with auth: {response.text}")
        print(f"Headers: {dict(response.headers)}")
        
    except Exception as e:
        print(f"Error with auth: {e}")

if __name__ == "__main__":
    test_endpoint() 