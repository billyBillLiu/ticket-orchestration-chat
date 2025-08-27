'''
LLM Service
Multi-provider LLM integration (Ollama, OpenAI)
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
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        self.temperature = settings.default_temperature
        self.max_tokens = settings.default_max_tokens
        
        # Configure provider-specific settings
        self._configure_provider()
        
        # Initialize HTTP client
        self.client = httpx.AsyncClient(timeout=30.0)
    
    def _configure_provider(self):
        """Configure provider-specific settings based on active provider"""
        if self.provider not in settings.available_providers:
            raise ValueError(f"Unsupported provider: {self.provider}")
        
        if self.provider == "ollama":
            self.base_url = settings.ollama_base_url
            self.api_key = None
        elif self.provider == "openai":
            self.base_url = settings.openai_base_url
            self.api_key = settings.openai_api_key
            if not self.api_key:
                raise ValueError(f"API key required for provider: {self.provider}")
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models from the active provider"""
        if self.provider == "ollama":
            return await self._list_ollama_models()
        elif self.provider == "openai":
            return await self._list_openai_models()
        else:
            logger.error(f"Unsupported provider for listing models: {self.provider}")
            return []
    
    async def _list_ollama_models(self) -> List[Dict[str, Any]]:
        """List available models from Ollama"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return data.get("models", [])
            else:
                logger.error(f"Failed to list Ollama models: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error listing Ollama models: {e}")
            return []
    
    async def _list_openai_models(self) -> List[Dict[str, Any]]:
        """List available models from OpenAI"""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = await self.client.get(f"{self.base_url}/models", headers=headers)
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            else:
                logger.error(f"Failed to list OpenAI models: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error listing OpenAI models: {e}")
            return []
    
    async def generate_response(
        self, 
        messages: List[Message], 
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response from the active provider"""
        model = model or self.model
        temperature = temperature or self.temperature
        max_tokens = max_tokens or self.max_tokens
        
        if self.provider == "ollama":
            async for chunk in self._generate_ollama_response(messages, model, temperature, max_tokens, stream):
                yield chunk
        elif self.provider == "openai":
            async for chunk in self._generate_openai_response(messages, model, temperature, max_tokens, stream):
                yield chunk
        else:
            error_msg = f"Unsupported provider: {self.provider}"
            logger.error(error_msg)
            yield f"Error: {error_msg}"
    
    async def _generate_ollama_response(
        self, 
        messages: List[Message], 
        model: str,
        temperature: float,
        max_tokens: int,
        stream: bool
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response from Ollama"""
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
                    yield f"Error: {error_msg}"
                    return
                
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                content = data["message"]["content"]
                                if content:
                                    yield content
                                    await asyncio.sleep(0)
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse JSON line: {line}")
                            continue
                        except Exception as e:
                            logger.error(f"Error processing stream line: {e}")
                            continue
                            
        except Exception as e:
            error_msg = f"Error generating Ollama response: {str(e)}"
            logger.error(error_msg)
            yield f"Error: {error_msg}"
    
    async def _generate_openai_response(
        self, 
        messages: List[Message], 
        model: str,
        temperature: float,
        max_tokens: int,
        stream: bool
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response from OpenAI"""
        # Convert messages to OpenAI format
        openai_messages = []
        for msg in messages:
            openai_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        payload = {
            "model": model,
            "messages": openai_messages,
            "stream": stream,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        logger.info(f"OpenAI request: model='{model}', messages={len(openai_messages)}")
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=60.0
            ) as response:
                if response.status_code != 200:
                    error_msg = f"OpenAI API error: {response.status_code}"
                    logger.error(error_msg)
                    yield f"Error: {error_msg}"
                    return
                
                async for line in response.aiter_lines():
                    if line.strip() and line.startswith("data: "):
                        try:
                            data_str = line[6:]  # Remove "data: " prefix
                            if data_str == "[DONE]":
                                break
                            data = json.loads(data_str)
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta and delta["content"]:
                                    yield delta["content"]
                                    await asyncio.sleep(0)
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse JSON line: {line}")
                            continue
                        except Exception as e:
                            logger.error(f"Error processing stream line: {e}")
                            continue
                            
        except Exception as e:
            error_msg = f"Error generating OpenAI response: {str(e)}"
            logger.error(error_msg)
            yield f"Error: {error_msg}"
    
    async def generate_non_streaming_response(
        self, 
        messages: List[Message], 
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> LLMResponse:
        """Generate non-streaming response from the active provider"""
        model = model or self.model
        temperature = temperature or self.temperature
        max_tokens = max_tokens or self.max_tokens
        
        if self.provider == "ollama":
            return await self._generate_ollama_non_streaming_response(messages, model, temperature, max_tokens)
        elif self.provider == "openai":
            return await self._generate_openai_non_streaming_response(messages, model, temperature, max_tokens)
        else:
            error_msg = f"Unsupported provider: {self.provider}"
            logger.error(error_msg)
            return LLMResponse(content=f"Error: {error_msg}", model=model)
    
    async def _generate_ollama_non_streaming_response(
        self, 
        messages: List[Message], 
        model: str,
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        """Generate non-streaming response from Ollama"""
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
                return LLMResponse(content=f"Error: {error_msg}", model=model)
                
        except Exception as e:
            error_msg = f"Error generating Ollama response: {str(e)}"
            logger.error(error_msg)
            return LLMResponse(content=f"Error: {error_msg}", model=model)
    
    async def _generate_openai_non_streaming_response(
        self, 
        messages: List[Message], 
        model: str,
        temperature: float,
        max_tokens: int
    ) -> LLMResponse:
        """Generate non-streaming response from OpenAI"""
        # Convert messages to OpenAI format
        openai_messages = []
        for msg in messages:
            openai_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        payload = {
            "model": model,
            "messages": openai_messages,
            "stream": False,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=60.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return LLMResponse(
                    content=data.get("choices", [{}])[0].get("message", {}).get("content", ""),
                    model=model,
                    usage=data.get("usage")
                )
            else:
                error_msg = f"OpenAI API error: {response.status_code}"
                logger.error(error_msg)
                return LLMResponse(content=f"Error: {error_msg}", model=model)
                
        except Exception as e:
            error_msg = f"Error generating OpenAI response: {str(e)}"
            logger.error(error_msg)
            return LLMResponse(content=f"Error: {error_msg}", model=model)
    
    async def health_check(self) -> bool:
        """Check if the active provider is running and accessible"""
        if self.provider == "ollama":
            return await self._ollama_health_check()
        elif self.provider == "openai":
            return await self._openai_health_check()
        else:
            logger.error(f"Unsupported provider for health check: {self.provider}")
            return False
    
    async def _ollama_health_check(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
    
    async def _openai_health_check(self) -> bool:
        """Check if OpenAI is accessible"""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = await self.client.get(f"{self.base_url}/models", headers=headers)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return False

# Create a singleton instance
llm_service = LLMService()

# Add synchronous chat function for the planner service
def chat(messages: list[dict], *, model: str, format: str | None = None, options: dict | None = None) -> str:
    """
    Call Ollama's /api/chat and return the message content as a string.
    If format='json', return the raw JSON string (not prettified).
    """
    import asyncio
    
    # Convert dict messages to Message objects
    message_objects = [Message(**msg) for msg in messages]
    
    # Extract options
    temperature = options.get("temperature", 0.7) if options else 0.7
    max_tokens = options.get("num_ctx", 1000) if options else 1000
    
    # Run the async function synchronously
    async def _async_chat():
        async with llm_service as service:
            response = await service.generate_non_streaming_response(
                messages=message_objects,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.content
    
    try:
        return asyncio.run(_async_chat())
    except Exception as e:
        logger.error(f"Error in synchronous chat: {e}")
        return f"Error: {str(e)}"

