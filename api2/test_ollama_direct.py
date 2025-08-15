#!/usr/bin/env python3
"""
Direct test of Ollama API
"""

import asyncio
import httpx
import json

async def test_ollama_direct():
    """Test Ollama API directly"""
    print("🧪 Testing Ollama API Directly...")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Test 1: Check if Ollama is running
        print("\n1. Testing Ollama availability...")
        try:
            response = await client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                print(f"✅ Ollama is running, found {len(models)} models:")
                for model in models:
                    print(f"   - {model.get('name')}")
            else:
                print(f"❌ Ollama returned {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Ollama test failed: {e}")
            return False
        
        # Test 2: Test chat API with deepseek-r1:8b
        print("\n2. Testing chat API...")
        try:
            payload = {
                "model": "deepseek-r1:8b",
                "messages": [
                    {"role": "user", "content": "Hello, can you respond with just 'Hi there!'?"}
                ],
                "stream": False
            }
            
            response = await client.post(
                "http://localhost:11434/api/chat",
                json=payload,
                timeout=30.0
            )
            
            print(f"   Status code: {response.status_code}")
            print(f"   Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Chat API worked!")
                print(f"   Response: {data.get('message', {}).get('content', 'No content')[:100]}...")
            else:
                print(f"❌ Chat API failed with status {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Chat API test failed: {e}")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 Ollama API tests completed!")
    return True

if __name__ == "__main__":
    print("🚀 Starting Direct Ollama API Tests")
    print()
    
    try:
        success = asyncio.run(test_ollama_direct())
        if success:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed!")
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
