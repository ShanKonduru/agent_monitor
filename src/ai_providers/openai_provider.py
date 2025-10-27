"""
OpenAI Provider Implementation for Phase 6.1
Handles OpenAI API integration with standardized interface
"""

import openai
import asyncio
from typing import List, Iterator, Dict, Any
from datetime import datetime
import time

from .base_provider import AIProvider, AIRequest, AIResponse, ModelInfo, ModelCapability

class OpenAIProvider(AIProvider):
    """OpenAI API provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("OpenAI", config)
        self.api_key = config.get('api_key')
        self.client = openai.AsyncOpenAI(api_key=self.api_key)
        
        # Model pricing (per 1K tokens)
        self.model_pricing = {
            'gpt-4': {'input': 0.03, 'output': 0.06},
            'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
            'gpt-3.5-turbo': {'input': 0.001, 'output': 0.002},
            'gpt-3.5-turbo-16k': {'input': 0.003, 'output': 0.004}
        }
        
    async def complete(self, request: AIRequest) -> AIResponse:
        """Generate text completion using OpenAI"""
        start_time = time.time()
        
        try:
            model = request.model or self.get_default_model()
            
            # Prepare messages
            messages = []
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})
            messages.append({"role": "user", "content": request.prompt})
            
            # Make API call
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=request.max_tokens or 1000,
                temperature=request.temperature,
                stream=False
            )
            
            # Calculate metrics
            latency_ms = int((time.time() - start_time) * 1000)
            tokens_used = response.usage.total_tokens
            cost = self.calculate_cost(tokens_used, model)
            
            return AIResponse(
                content=response.choices[0].message.content,
                model=model,
                provider=self.name,
                tokens_used=tokens_used,
                cost=cost,
                latency_ms=latency_ms,
                timestamp=datetime.now(),
                metadata={
                    'finish_reason': response.choices[0].finish_reason,
                    'usage': response.usage.model_dump()
                }
            )
            
        except Exception as e:
            self.is_healthy = False
            raise Exception(f"OpenAI completion failed: {str(e)}")
    
    async def stream_complete(self, request: AIRequest) -> Iterator[str]:
        """Generate streaming completion"""
        try:
            model = request.model or self.get_default_model()
            
            messages = []
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})
            messages.append({"role": "user", "content": request.prompt})
            
            stream = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=request.max_tokens or 1000,
                temperature=request.temperature,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            self.is_healthy = False
            raise Exception(f"OpenAI streaming failed: {str(e)}")
    
    async def get_models(self) -> List[ModelInfo]:
        """Get available OpenAI models"""
        try:
            models_response = await self.client.models.list()
            
            # Filter to chat models and add our known information
            chat_models = []
            model_configs = {
                'gpt-4': {
                    'max_tokens': 8192,
                    'context_window': 8192,
                    'capabilities': [ModelCapability.CHAT, ModelCapability.CODE_GENERATION, 
                                   ModelCapability.FUNCTION_CALLING, ModelCapability.STREAMING],
                    'description': 'Most capable GPT-4 model'
                },
                'gpt-4-turbo': {
                    'max_tokens': 4096,
                    'context_window': 128000,
                    'capabilities': [ModelCapability.CHAT, ModelCapability.CODE_GENERATION,
                                   ModelCapability.FUNCTION_CALLING, ModelCapability.STREAMING],
                    'description': 'Latest GPT-4 Turbo with vision'
                },
                'gpt-3.5-turbo': {
                    'max_tokens': 4096,
                    'context_window': 16385,
                    'capabilities': [ModelCapability.CHAT, ModelCapability.CODE_GENERATION,
                                   ModelCapability.FUNCTION_CALLING, ModelCapability.STREAMING],
                    'description': 'Fast and efficient chat model'
                }
            }
            
            for model in models_response.data:
                if model.id in model_configs:
                    config = model_configs[model.id]
                    chat_models.append(ModelInfo(
                        name=model.id,
                        provider=self.name,
                        max_tokens=config['max_tokens'],
                        capabilities=config['capabilities'],
                        cost_per_1k_tokens=self.model_pricing.get(model.id, {}).get('input', 0.001),
                        context_window=config['context_window'],
                        description=config['description']
                    ))
            
            return chat_models
            
        except Exception as e:
            self.is_healthy = False
            raise Exception(f"Failed to get OpenAI models: {str(e)}")
    
    async def health_check(self) -> bool:
        """Check OpenAI API health"""
        try:
            # Simple API call to check connectivity
            await self.client.models.list()
            self.is_healthy = True
            self.last_health_check = datetime.now()
            return True
            
        except Exception as e:
            self.is_healthy = False
            self.last_health_check = datetime.now()
            return False
    
    def calculate_cost(self, tokens: int, model: str) -> float:
        """Calculate OpenAI API cost"""
        pricing = self.model_pricing.get(model, {'input': 0.001, 'output': 0.002})
        # Simplified: assume 50/50 input/output split
        input_cost = (tokens * 0.5 / 1000) * pricing['input']
        output_cost = (tokens * 0.5 / 1000) * pricing['output']
        return input_cost + output_cost