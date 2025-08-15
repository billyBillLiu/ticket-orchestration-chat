import requests
import json
import uuid

def test_registration_response():
    """Test the registration endpoint with the new response format"""
    
    # Generate unique email to avoid conflicts
    unique_id = str(uuid.uuid4())[:8]
    
    # Test data
    test_user = {
        "email": f"test{unique_id}@example.com",
        "password": "testpassword123",
        "username": f"testuser{unique_id}",
        "name": "Test User",
        "role": "USER",
        "provider": "local"
    }
    
    # Make request to registration endpoint
    try:
        response = requests.post("http://localhost:8000/api/auth/register", json=test_user)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Check if response has the expected structure
        data = response.json()
        assert "success" in data, "Response should have 'success' field"
        assert "message" in data, "Response should have 'message' field"
        
        if data["success"]:
            assert "user" in data, "Success response should have 'user' field"
            print("✅ Success response format is correct")
        else:
            assert "error_type" in data, "Error response should have 'error_type' field"
            print("✅ Error response format is correct")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_registration_response() 