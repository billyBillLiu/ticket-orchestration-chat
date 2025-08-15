#!/usr/bin/env python3
"""
Test script for LLM service integration
Run this to verify Ollama is working with your setup
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.llm_service import llm_service, Message

async def test_llm_service():
    """Test the LLM service functionality"""
    print("🧪 Testing LLM Service Integration...")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. Testing health check...")
    try:
        is_healthy = await llm_service.health_check()
        if is_healthy:
            print("✅ Ollama is running and accessible")
        else:
            print("❌ Ollama is not responding")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 2: List Models
    print("\n2. Testing model listing...")
    try:
        models = await llm_service.list_models()
        if models:
            print(f"✅ Found {len(models)} models:")
            for model in models[:3]:  # Show first 3 models
                print(f"   - {model.get('name', 'Unknown')}")
        else:
            print("⚠️  No models found. You may need to pull a model:")
            print("   ollama pull deepseek-r1:8b")
    except Exception as e:
        print(f"❌ Model listing failed: {e}")
    
    # Test 3: Simple Response Generation
    print("\n3. Testing response generation...")
    try:
        messages = [
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="Hello! Can you help me with a simple question?")
        ]
        
        print("   Generating response...")
        response_content = ""
        async for chunk in llm_service.generate_response(messages=messages):
            response_content += chunk
            print(".", end="", flush=True)
        
        print(f"\n✅ Response generated ({len(response_content)} characters)")
        print(f"   Preview: {response_content[:100]}...")
        
    except Exception as e:
        print(f"\n❌ Response generation failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Your LLM service is working correctly.")
    return True

async def test_non_streaming():
    """Test non-streaming response generation"""
    print("\n4. Testing non-streaming response...")
    try:
        messages = [
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="What is 2+2?")
        ]
        
        response = await llm_service.generate_non_streaming_response(messages=messages)
        print(f"✅ Non-streaming response: {response.content}")
        
    except Exception as e:
        print(f"❌ Non-streaming test failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting LLM Service Tests")
    print("Make sure Ollama is running: ollama serve")
    print()
    
    try:
        success = asyncio.run(test_llm_service())
        if success:
            asyncio.run(test_non_streaming())
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)
