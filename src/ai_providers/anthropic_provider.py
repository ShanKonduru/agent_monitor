"""
Anthropic Provider Implementation for Phase 6.1
Handles Anthropic Claude API integration with standardized interface
"""

import anthropic
import asyncio
from typing import List, Iterator, Dict, Any
from datetime import datetime
import time

from .base_provider import AIProvider, AIRequest, AIResponse, ModelInfo, ModelCapability

class AnthropicProvider(AIProvider):
    """Anthropic Claude API provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("Anthropic", config)
        self.api_key = config.get('api_key')
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
        
        # Model pricing (per 1K tokens)
        self.model_pricing = {
            'claude-3-opus-20240229': {'input': 0.015, 'output': 0.075},
            'claude-3-sonnet-20240229': {'input': 0.003, 'output': 0.015},
            'claude-3-haiku-20240307': {'input': 0.00025, 'output': 0.00125},
            'claude-2.1': {'input': 0.008, 'output': 0.024},
            'claude-2.0': {'input': 0.008, 'output': 0.024}
        }
        
    async def complete(self, request: AIRequest) -> AIResponse:
        """Generate text completion using Anthropic Claude"""
        start_time = time.time()
        
        try:
            model = request.model or self.get_default_model()
            
            # Prepare message with system prompt
            message_content = request.prompt
            if request.system_prompt:
                message_content = f"System: {request.system_prompt}\n\nHuman: {request.prompt}"
            
            # Make API call
            response = await self.client.messages.create(
                model=model,
                max_tokens=request.max_tokens or 1000,
                temperature=request.temperature,
                messages=[{"role": "user", "content": message_content}]
            )
            
            # Calculate metrics
            latency_ms = int((time.time() - start_time) * 1000)
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            cost = self.calculate_cost(tokens_used, model)
            
            return AIResponse(
                content=response.content[0].text,
                model=model,
                provider=self.name,
                tokens_used=tokens_used,
                cost=cost,
                latency_ms=latency_ms,
                timestamp=datetime.now(),
                metadata={
                    'stop_reason': response.stop_reason,
                    'usage': {
                        'input_tokens': response.usage.input_tokens,
                        'output_tokens': response.usage.output_tokens
                    }
                }
            )
            
        except Exception as e:
            self.is_healthy = False
            raise Exception(f"Anthropic completion failed: {str(e)}")
    
    async def stream_complete(self, request: AIRequest) -> Iterator[str]:
        """Generate streaming completion"""
        try:
            model = request.model or self.get_default_model()
            
            message_content = request.prompt
            if request.system_prompt:
                message_content = f"System: {request.system_prompt}\n\nHuman: {request.prompt}"
            
            stream = await self.client.messages.create(
                model=model,
                max_tokens=request.max_tokens or 1000,
                temperature=request.temperature,
                messages=[{"role": "user", "content": message_content}],
                stream=True
            )
            
            async for chunk in stream:
                if chunk.type == "content_block_delta":
                    yield chunk.delta.text
                    
        except Exception as e:
            self.is_healthy = False
            raise Exception(f"Anthropic streaming failed: {str(e)}")
    
    async def get_models(self) -> List[ModelInfo]:
        """Get available Anthropic models"""
        # Anthropic doesn't have a models API, so we return known models
        models = [
            ModelInfo(
                name="claude-3-opus-20240229",
                provider=self.name,
                max_tokens=4096,
                capabilities=[ModelCapability.CHAT, ModelCapability.CODE_GENERATION, 
                             ModelCapability.STREAMING],
                cost_per_1k_tokens=0.015,
                context_window=200000,
                description="Most powerful Claude 3 model"
            ),
            ModelInfo(
                name="claude-3-sonnet-20240229", 
                provider=self.name,
                max_tokens=4096,
                capabilities=[ModelCapability.CHAT, ModelCapability.CODE_GENERATION,
                             ModelCapability.STREAMING],
                cost_per_1k_tokens=0.003,
                context_window=200000,
                description="Balanced Claude 3 model"
            ),
            ModelInfo(
                name="claude-3-haiku-20240307",
                provider=self.name,
                max_tokens=4096,
                capabilities=[ModelCapability.CHAT, ModelCapability.CODE_GENERATION,
                             ModelCapability.STREAMING],
                cost_per_1k_tokens=0.00025,
                context_window=200000,
                description="Fastest Claude 3 model"
            )
        ]
        
        return models
    
    async def health_check(self) -> bool:
        """Check Anthropic API health"""
        try:
            # Simple API call to check connectivity
            test_response = await self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}]
            )
            
            self.is_healthy = True
            self.last_health_check = datetime.now()
            return True
            
        except Exception as e:
            self.is_healthy = False
            self.last_health_check = datetime.now()
            return False
    
    def calculate_cost(self, tokens: int, model: str) -> float:
        """Calculate Anthropic API cost"""
        pricing = self.model_pricing.get(model, {'input': 0.008, 'output': 0.024})
        # Simplified: assume 50/50 input/output split
        input_cost = (tokens * 0.5 / 1000) * pricing['input']
        output_cost = (tokens * 0.5 / 1000) * pricing['output']
        return input_cost + output_cost