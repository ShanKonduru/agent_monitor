"""
Local LLM Provider Implementation for Phase 6.1
Handles local models (Ollama, LM Studio, etc.) with standardized interface
"""

import aiohttp
import asyncio
from typing import List, Iterator, Dict, Any
from datetime import datetime
import time
import json

from .base_provider import AIProvider, AIRequest, AIResponse, ModelInfo, ModelCapability

class LocalLLMProvider(AIProvider):
    """Local LLM provider implementation (supports Ollama, LM Studio, etc.)"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("LocalLLM", config)
        self.base_url = config.get('base_url', 'http://localhost:11434')  # Default Ollama port
        self.provider_type = config.get('provider_type', 'ollama')  # ollama, lmstudio, etc.
        
    async def complete(self, request: AIRequest) -> AIResponse:
        """Generate text completion using local LLM"""
        start_time = time.time()
        
        try:
            model = request.model or self.get_default_model()
            
            # Prepare prompt with system instruction
            full_prompt = request.prompt
            if request.system_prompt:
                full_prompt = f"{request.system_prompt}\n\n{request.prompt}"
            
            # Prepare API payload based on provider type
            if self.provider_type == 'ollama':
                payload = {
                    "model": model,
                    "prompt": full_prompt,
                    "options": {
                        "temperature": request.temperature,
                        "num_predict": request.max_tokens or 1000
                    },
                    "stream": False
                }
                endpoint = f"{self.base_url}/api/generate"
                
            elif self.provider_type == 'lmstudio':
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": full_prompt}],
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens or 1000,
                    "stream": False
                }
                endpoint = f"{self.base_url}/v1/chat/completions"
            
            else:
                raise Exception(f"Unsupported local provider type: {self.provider_type}")
            
            # Make API call
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, json=payload) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}: {await response.text()}")
                    
                    result = await response.json()
            
            # Parse response based on provider type
            if self.provider_type == 'ollama':
                content = result.get('response', '')
                tokens_used = len(content.split())  # Approximate
                
            elif self.provider_type == 'lmstudio':
                content = result['choices'][0]['message']['content']
                tokens_used = result.get('usage', {}).get('total_tokens', len(content.split()))
            
            # Calculate metrics
            latency_ms = int((time.time() - start_time) * 1000)
            cost = 0.0  # Local models are free
            
            return AIResponse(
                content=content,
                model=model,
                provider=self.name,
                tokens_used=tokens_used,
                cost=cost,
                latency_ms=latency_ms,
                timestamp=datetime.now(),
                metadata={
                    'provider_type': self.provider_type,
                    'local_inference': True
                }
            )
            
        except Exception as e:
            self.is_healthy = False
            raise Exception(f"Local LLM completion failed: {str(e)}")
    
    async def stream_complete(self, request: AIRequest) -> Iterator[str]:
        """Generate streaming completion"""
        try:
            model = request.model or self.get_default_model()
            
            full_prompt = request.prompt
            if request.system_prompt:
                full_prompt = f"{request.system_prompt}\n\n{request.prompt}"
            
            if self.provider_type == 'ollama':
                payload = {
                    "model": model,
                    "prompt": full_prompt,
                    "options": {
                        "temperature": request.temperature,
                        "num_predict": request.max_tokens or 1000
                    },
                    "stream": True
                }
                endpoint = f"{self.base_url}/api/generate"
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(endpoint, json=payload) as response:
                        async for line in response.content:
                            if line:
                                try:
                                    chunk = json.loads(line.decode())
                                    if 'response' in chunk:
                                        yield chunk['response']
                                except json.JSONDecodeError:
                                    continue
                                    
        except Exception as e:
            self.is_healthy = False
            raise Exception(f"Local LLM streaming failed: {str(e)}")
    
    async def get_models(self) -> List[ModelInfo]:
        """Get available local models"""
        try:
            if self.provider_type == 'ollama':
                endpoint = f"{self.base_url}/api/tags"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(endpoint) as response:
                        if response.status != 200:
                            return []
                        
                        result = await response.json()
                        models = []
                        
                        for model_data in result.get('models', []):
                            models.append(ModelInfo(
                                name=model_data['name'],
                                provider=self.name,
                                max_tokens=2048,  # Default for local models
                                capabilities=[ModelCapability.CHAT, ModelCapability.STREAMING],
                                cost_per_1k_tokens=0.0,  # Free
                                context_window=4096,  # Default
                                description=f"Local Ollama model: {model_data['name']}"
                            ))
                        
                        return models
                        
            elif self.provider_type == 'lmstudio':
                endpoint = f"{self.base_url}/v1/models"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(endpoint) as response:
                        if response.status != 200:
                            return []
                        
                        result = await response.json()
                        models = []
                        
                        for model_data in result.get('data', []):
                            models.append(ModelInfo(
                                name=model_data['id'],
                                provider=self.name,
                                max_tokens=2048,
                                capabilities=[ModelCapability.CHAT, ModelCapability.STREAMING],
                                cost_per_1k_tokens=0.0,
                                context_window=4096,
                                description=f"Local LM Studio model: {model_data['id']}"
                            ))
                        
                        return models
            
            return []
            
        except Exception as e:
            self.is_healthy = False
            return []
    
    async def health_check(self) -> bool:
        """Check local LLM service health"""
        try:
            if self.provider_type == 'ollama':
                endpoint = f"{self.base_url}/api/tags"
            elif self.provider_type == 'lmstudio':
                endpoint = f"{self.base_url}/v1/models"
            else:
                return False
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint) as response:
                    if response.status == 200:
                        self.is_healthy = True
                        self.last_health_check = datetime.now()
                        return True
                    
            return False
            
        except Exception as e:
            self.is_healthy = False
            self.last_health_check = datetime.now()
            return False
    
    def calculate_cost(self, tokens: int, model: str) -> float:
        """Local models are free"""
        return 0.0