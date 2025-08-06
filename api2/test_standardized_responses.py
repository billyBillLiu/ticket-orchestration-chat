#!/usr/bin/env python3
"""
Test script to demonstrate standardized responses for the registration endpoint.
This shows how the new response system handles different scenarios.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_successful_registration():
    """Test successful user registration"""
    print("=== Testing Successful Registration ===")
    
    data = {
        "email": "test@example.com",
        "password": "password123",
        "username": "testuser",
        "name": "Test User"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_duplicate_user():
    """Test registration with existing user"""
    print("=== Testing Duplicate User Registration ===")
    
    data = {
        "email": "test@example.com",
        "password": "password123",
        "username": "testuser"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_invalid_email():
    """Test registration with invalid email (should trigger validation error)"""
    print("=== Testing Invalid Email (Validation Error) ===")
    
    data = {
        "email": "invalid-email",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_missing_required_fields():
    """Test registration with missing required fields"""
    print("=== Testing Missing Required Fields ===")
    
    data = {
        "email": "test2@example.com"
        # Missing password
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_invalid_email_format():
    """Test registration with invalid email format"""
    print("=== Testing Invalid Email Format ===")
    
    data = {
        "email": "test@test.test",  # This should trigger validation error
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

if __name__ == "__main__":
    print("Testing Standardized Response System")
    print("=" * 50)
    print()
    
    # Run tests
    test_successful_registration()
    test_duplicate_user()
    test_invalid_email()
    test_missing_required_fields()
    test_invalid_email_format()
    
    print("All tests completed!") 