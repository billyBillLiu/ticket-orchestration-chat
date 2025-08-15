#!/usr/bin/env python3
"""
Test script for chat endpoint
"""

import asyncio
import sys
import os
import httpx
import json

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_chat_endpoint():
    """Test the chat endpoint"""
    print("🧪 Testing Chat Endpoint...")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Test 1: Health check
        print("\n1. Testing health check...")
        try:
            response = await client.get("http://127.0.0.1:3080/health")
            if response.status_code == 200:
                print("✅ Server is running")
            else:
                print(f"❌ Server returned {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
        
        # Test 2: LLM health check
        print("\n2. Testing LLM health check...")
        try:
            response = await client.get("http://127.0.0.1:3080/api/llm/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ LLM health: {data.get('status')}")
                print(f"   Model: {data.get('default_model')}")
            else:
                print(f"❌ LLM health check returned {response.status_code}")
        except Exception as e:
            print(f"❌ LLM health check failed: {e}")
        
        # Test 3: Chat endpoint
        print("\n3. Testing chat endpoint...")
        try:
            chat_data = {
                "messages": [
                    {"role": "user", "content": "Hello! Can you help me with a simple question?"}
                ],
                "model": "deepseek-r1:8b",
                "conversationId": "00000000-0000-0000-0000-000000000000"
            }
            
            response = await client.post(
                "http://127.0.0.1:3080/api/ask/custom",
                json=chat_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print("✅ Chat endpoint responded successfully")
                # The response should be a streaming response
                print(f"   Response type: {response.headers.get('content-type')}")
            else:
                print(f"❌ Chat endpoint returned {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Chat endpoint test failed: {e}")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 Chat endpoint tests completed!")
    return True

if __name__ == "__main__":
    print("🚀 Starting Chat Endpoint Tests")
    print("Make sure the server is running: python -m uvicorn main:app --host 127.0.0.1 --port 3080")
    print()
    
    try:
        success = asyncio.run(test_chat_endpoint())
        if success:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)
