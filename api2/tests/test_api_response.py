#!/usr/bin/env python3
"""Test file for ApiResponse class methods"""

from app.utils.response_utils import ApiResponse

def test_api_response():
    print("Testing ApiResponse class methods...")
    
    # Test 1: Direct instantiation
    print("\n1. Direct instantiation:")
    response1 = ApiResponse(success=True, message="Test", data={"test": "data"})
    print(response1.model_dump_json())
    
    # Test 2: Class method
    print("\n2. Class method create_success():")
    try:
        response2 = ApiResponse.create_success({"test": "data"}, "Success test")
        print(response2.model_dump_json())
    except Exception as e:
        print(f"Error: {e}")
        print(f"Type: {type(e)}")
    
    # Test 3: Error method
    print("\n3. Class method create_error():")
    try:
        response3 = ApiResponse.create_error("Test error", "TEST_ERROR")
        print(response3.model_dump_json())
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Check if methods exist
    print("\n4. Checking if methods exist:")
    print(f"hasattr(ApiResponse, 'create_success'): {hasattr(ApiResponse, 'create_success')}")
    print(f"hasattr(ApiResponse, 'create_error'): {hasattr(ApiResponse, 'create_error')}")
    print(f"dir(ApiResponse): {[attr for attr in dir(ApiResponse) if not attr.startswith('_')]}")

if __name__ == "__main__":
    test_api_response() 