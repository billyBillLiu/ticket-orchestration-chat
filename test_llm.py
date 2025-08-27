import asyncio
from app.services.llm_service import llm_service, Message

async def test_llm():
    print("Testing LLM service...")
    
    # Test health check
    health = await llm_service.health_check()
    print(f"Health check: {health}")
    
    if health:
        # Test a simple chat
        messages = [Message(role="user", content="Hello, how are you?")]
        try:
            response = await llm_service.generate_non_streaming_response(
                messages=messages,
                model="llama3:8b",
                temperature=0.7,
                max_tokens=100
            )
            print(f"LLM Response: {response.content}")
        except Exception as e:
            print(f"LLM Error: {e}")
    else:
        print("LLM health check failed")

if __name__ == "__main__":
    asyncio.run(test_llm())
