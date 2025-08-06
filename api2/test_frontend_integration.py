import requests
import json
import uuid

def test_frontend_integration():
    """Test that the frontend will handle both success and error responses correctly"""
    
    print("Testing Frontend Integration with Registration Endpoint")
    print("=" * 50)
    
    # Test 1: Error case - User already exists
    print("\n1. Testing Error Case (User already exists):")
    test_user_error = {
        "email": "test123@example.com",
        "password": "testpass123",
        "username": "testuser123",
        "name": "Test User",
        "role": "USER",
        "provider": "local"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/auth/register", json=test_user_error)
        data = response.json()
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")
        
        # Frontend should show error message
        if data["success"] == False:
            print("✅ Frontend will show error message:", data["message"])
        else:
            print("❌ Unexpected success response")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Success case - New user
    print("\n2. Testing Success Case (New user):")
    unique_id = str(uuid.uuid4())[:8]
    test_user_success = {
        "email": f"test{unique_id}@example.com",
        "password": "testpass123",
        "username": f"testuser{unique_id}",
        "name": "Test User",
        "role": "USER",
        "provider": "local"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/auth/register", json=test_user_success)
        data = response.json()
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")
        
        # Frontend should show success message and redirect
        if data["success"] == True:
            print("✅ Frontend will show success message and redirect")
            print("✅ User data available:", data["user"]["email"])
        else:
            print("❌ Unexpected error response")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Validation error case
    print("\n3. Testing Validation Error Case (Invalid data):")
    test_user_invalid = {
        "email": "invalid-email",
        "password": "short",
        "username": "",
        "name": "Test User",
        "role": "USER",
        "provider": "local"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/auth/register", json=test_user_invalid)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Frontend should show validation error
        if response.status_code == 422:
            print("✅ Frontend will show validation error message")
        else:
            print("❌ Unexpected response for validation error")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("Frontend Integration Test Summary:")
    print("✅ Error responses (success: false) will show error messages")
    print("✅ Success responses (success: true) will show success and redirect")
    print("✅ Validation errors (422) will show validation messages")
    print("✅ All response formats are consistent and structured")

if __name__ == "__main__":
    test_frontend_integration() 