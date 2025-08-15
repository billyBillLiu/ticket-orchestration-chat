'''
LLM Service
Ollama client integration
Model management
Streaming response handling
Error handling and fallbacks
'''

import asyncio
import json
import logging
from typing import AsyncGenerator, Dict, List, Optional, Any
from pydantic import BaseModel
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

class Message(BaseModel):
    role: str
    content: str

class LLMRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000
    stream: bool = True

class LLMResponse(BaseModel):
    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None

class LLMService:
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.default_model = settings.default_model
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models from Ollama"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return data.get("models", [])
            else:
                logger.error(f"Failed to list models: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    async def generate_response(
        self, 
        messages: List[Message], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response from Ollama"""
        model = model or self.default_model
        
        # Convert messages to Ollama format
        ollama_messages = []
        for msg in messages:
            ollama_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        payload = {
            "model": model,
            "messages": ollama_messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        # Log Ollama request
        logger.info(f"Ollama request: model='{model}', messages={len(ollama_messages)}")
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=60.0
            ) as response:
                if response.status_code != 200:
                    error_msg = f"Ollama API error: {response.status_code}"
                    logger.error(error_msg)
                    logger.error(f"Response text: {response.text}")
                    logger.error(f"Request payload: {payload}")
                    yield f"Error: {error_msg}"
                    return
                
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                content = data["message"]["content"]
                                if content:
                                    # Yield immediately without any buffering
                                    yield content
                                    # Force immediate flush if possible
                                    await asyncio.sleep(0)  # Yield control to event loop
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse JSON line: {line}")
                            continue
                        except Exception as e:
                            logger.error(f"Error processing stream line: {e}")
                            continue
                            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            logger.error(error_msg)
            yield f"Error: {error_msg}"
    
    async def generate_non_streaming_response(
        self, 
        messages: List[Message], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> LLMResponse:
        """Generate non-streaming response from Ollama"""
        model = model or self.default_model
        
        # Convert messages to Ollama format
        ollama_messages = []
        for msg in messages:
            ollama_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        payload = {
            "model": model,
            "messages": ollama_messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=60.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return LLMResponse(
                    content=data.get("message", {}).get("content", ""),
                    model=model,
                    usage=data.get("usage")
                )
            else:
                error_msg = f"Ollama API error: {response.status_code}"
                logger.error(error_msg)
                return LLMResponse(
                    content=f"Error: {error_msg}",
                    model=model
                )
                
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            logger.error(error_msg)
            return LLMResponse(
                content=f"Error: {error_msg}",
                model=model
            )
    
    async def health_check(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

# Create a singleton instance
llm_service = LLMService()

