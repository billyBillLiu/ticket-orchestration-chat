#!/usr/bin/env python3
"""
Simple test script to verify DELETE conversation endpoints
Run this script to test the conversation deletion functionality
"""

import requests
import json
import sys
import os

# Add the api2 directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api2'))

# Configuration
BASE_URL = "http://localhost:3080"
API_BASE = f"{BASE_URL}/api"

def test_delete_conversations():
    """Test the DELETE conversation endpoints"""
    
    print("Testing DELETE conversation endpoints...")
    print("=" * 50)
    
    # Test 1: Delete specific conversation by ID (query params)
    print("\n1. Testing DELETE /api/convos/ with conversationId (query params)")
    try:
        # Note: You'll need to replace '123' with an actual conversation ID from your database
        response = requests.delete(f"{API_BASE}/convos/", params={
            "conversationId": "123"
        })
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 1b: Delete specific conversation by ID (request body - like frontend)
    print("\n1b. Testing DELETE /api/convos/ with conversationId (request body)")
    try:
        # Note: You'll need to replace '123' with an actual conversation ID from your database
        payload = {
            "arg": {
                "conversationId": "123",
                "source": "button"
            }
        }
        response = requests.delete(f"{API_BASE}/convos/", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 1c: Delete specific conversation by ID (exact frontend payload format)
    print("\n1c. Testing DELETE /api/convos/ with exact frontend payload format")
    try:
        # This matches the exact payload format from the user's error
        payload = {
            "arg": {
                "conversationId": "9",
                "endpoint": "openAI",
                "source": "button"
            }
        }
        response = requests.delete(f"{API_BASE}/convos/", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Delete conversations by thread_id
    print("\n2. Testing DELETE /api/convos/ with thread_id")
    try:
        response = requests.delete(f"{API_BASE}/convos/", params={
            "thread_id": "test_thread_123"
        })
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Delete conversations by endpoint
    print("\n3. Testing DELETE /api/convos/ with endpoint")
    try:
        response = requests.delete(f"{API_BASE}/convos/", params={
            "endpoint": "openai"
        })
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Delete all conversations
    print("\n4. Testing DELETE /api/convos/all")
    try:
        response = requests.delete(f"{API_BASE}/convos/all")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: Test error case - no parameters
    print("\n5. Testing DELETE /api/convos/ with no parameters (should return 400)")
    try:
        response = requests.delete(f"{API_BASE}/convos/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_delete_conversations()
