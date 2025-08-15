#!/usr/bin/env python3
"""
Simple test to verify DELETE endpoint works
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:3080"
API_BASE = f"{BASE_URL}/api"

def test_delete_endpoint():
    """Test the DELETE endpoint with the exact payload from the user"""
    
    print("Testing DELETE /api/convos/ endpoint...")
    print("=" * 50)
    
    # Test with the exact payload that was causing 405 error
    payload = {
        "arg": {
            "conversationId": "9",
            "endpoint": "openAI",
            "source": "button"
        }
    }
    
    try:
        response = requests.delete(f"{API_BASE}/convos/", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 401:
            print("✅ SUCCESS: Endpoint is working! 401 is expected without authentication.")
            print("The 405 Method Not Allowed error is fixed!")
        elif response.status_code == 200:
            print("✅ SUCCESS: Endpoint is working and authenticated!")
        else:
            print(f"⚠️  Status {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_delete_endpoint()
