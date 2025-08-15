#!/usr/bin/env python3
"""
Very simple test to check if the endpoint is working
"""
import requests

def test_endpoint():
    """Test if the endpoint is accessible"""
    print("Testing endpoint accessibility...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health")
        print(f"Health endpoint status: {response.status_code}")
        print(f"Health response: {response.text}")
        
        # Test endpoints endpoint
        response = requests.get("http://localhost:8000/api/endpoints")
        print(f"Endpoints status: {response.status_code}")
        print(f"Endpoints response: {response.text}")
        
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_endpoint() 