#!/usr/bin/env python3
"""
Test script for the conversation memory implementation.
This script tests the memory service and API endpoints.
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_memory_endpoints():
    """Test the memory-related endpoints"""
    
    print("🧪 Testing Conversation Memory Implementation")
    print("=" * 50)
    
    # Test 1: Get memory stats
    print("\n1. Testing Memory Stats...")
    try:
        response = requests.get(f"{API_BASE}/memory/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Memory stats retrieved successfully")
            print(f"   - Total conversations: {stats['conversations']['total']}")
            print(f"   - Active conversations: {stats['conversations']['active']}")
            print(f"   - Total messages: {stats['messages']['total']}")
        else:
            print(f"❌ Failed to get memory stats: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing memory stats: {e}")
    
    # Test 2: Get user memory
    print("\n2. Testing User Memory...")
    try:
        response = requests.get(f"{API_BASE}/memory/user/memory?limit=5")
        if response.status_code == 200:
            memory = response.json()
            print(f"✅ User memory retrieved successfully")
            print(f"   - Recent conversations: {memory['total_conversations']}")
            if memory['conversations']:
                latest = memory['conversations'][0]
                print(f"   - Latest conversation: {latest['title']}")
        else:
            print(f"❌ Failed to get user memory: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing user memory: {e}")
    
    # Test 3: Get conversation summary (if conversations exist)
    print("\n3. Testing Conversation Summary...")
    try:
        # First get user memory to find a conversation ID
        response = requests.get(f"{API_BASE}/memory/user/memory?limit=1")
        if response.status_code == 200:
            memory = response.json()
            if memory['conversations']:
                conv_id = memory['conversations'][0]['conversation_id']
                response = requests.get(f"{API_BASE}/memory/summary/{conv_id}")
                if response.status_code == 200:
                    summary = response.json()
                    print(f"✅ Conversation summary retrieved successfully")
                    print(f"   - Conversation: {summary['title']}")
                    print(f"   - Total messages: {summary['total_messages']}")
                    print(f"   - User messages: {summary['user_messages']}")
                    print(f"   - Assistant messages: {summary['assistant_messages']}")
                else:
                    print(f"❌ Failed to get conversation summary: {response.status_code}")
            else:
                print("⚠️  No conversations found to test summary")
        else:
            print(f"❌ Failed to get user memory for summary test: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing conversation summary: {e}")
    
    # Test 4: Get conversation context (if conversations exist)
    print("\n4. Testing Conversation Context...")
    try:
        # First get user memory to find a conversation ID
        response = requests.get(f"{API_BASE}/memory/user/memory?limit=1")
        if response.status_code == 200:
            memory = response.json()
            if memory['conversations']:
                conv_id = memory['conversations'][0]['conversation_id']
                response = requests.get(f"{API_BASE}/memory/context/{conv_id}?max_messages=5")
                if response.status_code == 200:
                    context = response.json()
                    print(f"✅ Conversation context retrieved successfully")
                    print(f"   - Conversation: {context['conversation_title']}")
                    print(f"   - Messages in context: {context['message_count']}")
                    print(f"   - Context messages: {len(context['messages'])}")
                else:
                    print(f"❌ Failed to get conversation context: {response.status_code}")
            else:
                print("⚠️  No conversations found to test context")
        else:
            print(f"❌ Failed to get user memory for context test: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing conversation context: {e}")
    
    # Test 5: Search memory
    print("\n5. Testing Memory Search...")
    try:
        response = requests.get(f"{API_BASE}/memory/search?query=hello&limit=5")
        if response.status_code == 200:
            search_results = response.json()
            print(f"✅ Memory search completed successfully")
            print(f"   - Query: {search_results['query']}")
            print(f"   - Results found: {search_results['total_results']}")
        else:
            print(f"❌ Failed to search memory: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing memory search: {e}")
    
    # Test 6: Get conversation timeline (if conversations exist)
    print("\n6. Testing Conversation Timeline...")
    try:
        # First get user memory to find a conversation ID
        response = requests.get(f"{API_BASE}/memory/user/memory?limit=1")
        if response.status_code == 200:
            memory = response.json()
            if memory['conversations']:
                conv_id = memory['conversations'][0]['conversation_id']
                response = requests.get(f"{API_BASE}/memory/timeline/{conv_id}")
                if response.status_code == 200:
                    timeline = response.json()
                    print(f"✅ Conversation timeline retrieved successfully")
                    print(f"   - Total messages in timeline: {timeline['total_messages']}")
                    if timeline['timeline']:
                        first_msg = timeline['timeline'][0]
                        print(f"   - First message: {first_msg['role']} - {first_msg['content'][:50]}...")
                else:
                    print(f"❌ Failed to get conversation timeline: {response.status_code}")
            else:
                print("⚠️  No conversations found to test timeline")
        else:
            print(f"❌ Failed to get user memory for timeline test: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing conversation timeline: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Memory implementation testing completed!")

def test_message_endpoints():
    """Test the message-related endpoints"""
    
    print("\n🧪 Testing Message Endpoints")
    print("=" * 50)
    
    # Test 1: Get messages for a conversation
    print("\n1. Testing Get Messages...")
    try:
        # First get user memory to find a conversation ID
        response = requests.get(f"{API_BASE}/memory/user/memory?limit=1")
        if response.status_code == 200:
            memory = response.json()
            if memory['conversations']:
                conv_id = memory['conversations'][0]['conversation_id']
                response = requests.get(f"{API_BASE}/convos/{conv_id}/messages?limit=10")
                if response.status_code == 200:
                    messages = response.json()
                    print(f"✅ Messages retrieved successfully")
                    print(f"   - Total messages: {messages['total']}")
                    print(f"   - Messages returned: {len(messages['messages'])}")
                else:
                    print(f"❌ Failed to get messages: {response.status_code}")
            else:
                print("⚠️  No conversations found to test messages")
        else:
            print(f"❌ Failed to get user memory for messages test: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing get messages: {e}")

if __name__ == "__main__":
    print("🚀 Starting Memory Implementation Tests")
    print("Make sure your FastAPI server is running on http://localhost:8000")
    print("You may need to authenticate first if endpoints require authentication")
    
    # Wait a moment for user to read
    time.sleep(2)
    
    # Run tests
    test_memory_endpoints()
    test_message_endpoints()
    
    print("\n📝 Next Steps:")
    print("1. Add authentication if endpoints require it")
    print("2. Test with real OpenAI API integration")
    print("3. Implement frontend integration")
    print("4. Add more advanced memory features (embeddings, semantic search)") 