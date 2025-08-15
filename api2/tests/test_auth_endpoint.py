#!/usr/bin/env python3
"""
Test authentication endpoint
"""
import requests
import json

def test_auth():
    """Test authentication endpoint"""
    print("Testing authentication endpoint...")
    
    try:
        # Test login endpoint
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = requests.post(
            "http://localhost:8000/api/auth/login",
            json=login_data
        )
        
        print(f"Login status: {response.status_code}")
        print(f"Login response: {response.text}")
        
        if response.status_code == 200:
            # Test user endpoint with token
            token_data = response.json()
            token = token_data.get("access_token")
            
            headers = {
                "Authorization": f"Bearer {token}"
            }
            
            user_response = requests.get(
                "http://localhost:8000/api/user",
                headers=headers
            )
            
            print(f"User endpoint status: {user_response.status_code}")
            print(f"User response: {user_response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_auth() 