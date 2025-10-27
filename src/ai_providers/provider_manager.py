"""
AI Provider Manager for Phase 6.1
Manages multiple AI providers with load balancing, failover, and monitoring
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import random
import logging

from .base_provider import AIProvider, AIRequest, AIResponse, ModelInfo
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .local_provider import LocalLLMProvider

logger = logging.getLogger(__name__)

class AIProviderManager:
    """Manages multiple AI providers with intelligent routing"""
    
    def __init__(self, config: Dict[str, Any]):
        self.providers: Dict[str, AIProvider] = {}
        self.config = config
        self.default_provider = None
        self.health_check_interval = 300  # 5 minutes
        self.last_health_check = datetime.now()
        
        # Load balancing configuration
        self.load_balance_strategy = config.get('load_balance_strategy', 'round_robin')
        self.current_provider_index = 0
        
        # Performance tracking
        self.provider_stats = {}
        
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize AI providers based on configuration"""
        provider_configs = self.config.get('providers', {})
        
        # Initialize OpenAI provider
        if 'openai' in provider_configs:
            try:
                self.providers['openai'] = OpenAIProvider(provider_configs['openai'])
                logger.info("OpenAI provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI provider: {e}")
        
        # Initialize Anthropic provider
        if 'anthropic' in provider_configs:
            try:
                self.providers['anthropic'] = AnthropicProvider(provider_configs['anthropic'])
                logger.info("Anthropic provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic provider: {e}")
        
        # Initialize Local LLM provider
        if 'local' in provider_configs:
            try:
                self.providers['local'] = LocalLLMProvider(provider_configs['local'])
                logger.info("Local LLM provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Local LLM provider: {e}")
        
        # Set default provider
        if self.providers:
            self.default_provider = list(self.providers.keys())[0]
            logger.info(f"Default provider set to: {self.default_provider}")
        
        # Initialize stats tracking
        for provider_name in self.providers:
            self.provider_stats[provider_name] = {
                'requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'total_latency': 0,
                'total_tokens': 0,
                'total_cost': 0
            }
    
    async def complete(self, request: AIRequest, provider_name: Optional[str] = None) -> AIResponse:
        """Route completion request to appropriate provider"""
        
        # Determine which provider to use
        if provider_name and provider_name in self.providers:
            provider = self.providers[provider_name]
        else:
            provider = await self._select_provider(request)
        
        if not provider:
            raise Exception("No healthy providers available")
        
        # Update stats - find the correct provider key
        provider_key = None
        for key, prov in self.providers.items():
            if prov == provider:
                provider_key = key
                break
                
        if provider_key is None:
            # Fallback to mapping provider name to key
            provider_name_lower = provider.name.lower()
            if 'openai' in provider_name_lower:
                provider_key = 'openai'
            elif 'anthropic' in provider_name_lower:
                provider_key = 'anthropic'
            elif 'local' in provider_name_lower:
                provider_key = 'local'
            else:
                provider_key = list(self.providers.keys())[0]  # Fallback
                
        self.provider_stats[provider_key]['requests'] += 1
        
        try:
            # Make the request
            response = await provider.complete(request)
            
            # Update success stats
            self.provider_stats[provider_key]['successful_requests'] += 1
            self.provider_stats[provider_key]['total_latency'] += response.latency_ms
            self.provider_stats[provider_key]['total_tokens'] += response.tokens_used
            self.provider_stats[provider_key]['total_cost'] += response.cost
            
            return response
            
        except Exception as e:
            # Update failure stats
            self.provider_stats[provider_key]['failed_requests'] += 1
            logger.error(f"Provider {provider.name} failed: {e}")
            
            # Try fallback provider if available
            fallback_provider = await self._get_fallback_provider(provider.name)
            if fallback_provider:
                logger.info(f"Falling back to {fallback_provider.name}")
                return await self.complete(request, fallback_provider.name.lower())
            
            raise e
    
    async def stream_complete(self, request: AIRequest, provider_name: Optional[str] = None):
        """Route streaming completion request to appropriate provider"""
        
        if provider_name and provider_name in self.providers:
            provider = self.providers[provider_name]
        else:
            provider = await self._select_provider(request)
        
        if not provider:
            raise Exception("No healthy providers available")
        
        async for chunk in provider.stream_complete(request):
            yield chunk
    
    async def get_all_models(self) -> Dict[str, List[ModelInfo]]:
        """Get models from all providers"""
        all_models = {}
        
        for provider_name, provider in self.providers.items():
            try:
                models = await provider.get_models()
                all_models[provider_name] = models
            except Exception as e:
                logger.error(f"Failed to get models from {provider_name}: {e}")
                all_models[provider_name] = []
        
        return all_models
    
    async def switch_default_provider(self, provider_name: str) -> bool:
        """Switch the default provider"""
        if provider_name in self.providers:
            self.default_provider = provider_name
            logger.info(f"Default provider switched to: {provider_name}")
            return True
        return False
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all providers"""
        health_status = {}
        
        for provider_name, provider in self.providers.items():
            try:
                is_healthy = await provider.health_check()
                health_status[provider_name] = is_healthy
                logger.info(f"Provider {provider_name} health: {'OK' if is_healthy else 'FAILED'}")
            except Exception as e:
                health_status[provider_name] = False
                logger.error(f"Health check failed for {provider_name}: {e}")
        
        self.last_health_check = datetime.now()
        return health_status
    
    async def get_provider_stats(self) -> Dict[str, Dict]:
        """Get performance statistics for all providers"""
        stats = {}
        
        for provider_name, raw_stats in self.provider_stats.items():
            stats[provider_name] = raw_stats.copy()
            
            # Calculate derived metrics
            if raw_stats['successful_requests'] > 0:
                stats[provider_name]['avg_latency'] = raw_stats['total_latency'] / raw_stats['successful_requests']
                stats[provider_name]['avg_tokens_per_request'] = raw_stats['total_tokens'] / raw_stats['successful_requests']
                stats[provider_name]['avg_cost_per_request'] = raw_stats['total_cost'] / raw_stats['successful_requests']
                stats[provider_name]['success_rate'] = raw_stats['successful_requests'] / raw_stats['requests']
            else:
                stats[provider_name].update({
                    'avg_latency': 0,
                    'avg_tokens_per_request': 0,
                    'avg_cost_per_request': 0,
                    'success_rate': 0
                })
        
        return stats
    
    async def _select_provider(self, request: AIRequest) -> Optional[AIProvider]:
        """Select best provider based on load balancing strategy"""
        
        # Get healthy providers
        healthy_providers = []
        for provider_name, provider in self.providers.items():
            if provider.is_healthy:
                healthy_providers.append(provider)
        
        if not healthy_providers:
            # Perform health check if all seem unhealthy
            await self.health_check_all()
            healthy_providers = [p for p in self.providers.values() if p.is_healthy]
        
        if not healthy_providers:
            return None
        
        # Apply load balancing strategy
        if self.load_balance_strategy == 'round_robin':
            provider = healthy_providers[self.current_provider_index % len(healthy_providers)]
            self.current_provider_index += 1
            return provider
            
        elif self.load_balance_strategy == 'random':
            return random.choice(healthy_providers)
            
        elif self.load_balance_strategy == 'least_latency':
            # Choose provider with lowest average latency
            best_provider = None
            best_latency = float('inf')
            
            for provider in healthy_providers:
                provider_name = provider.name.lower().replace(' ', '_')
                stats = self.provider_stats.get(provider_name, {})
                
                if stats.get('successful_requests', 0) > 0:
                    avg_latency = stats['total_latency'] / stats['successful_requests']
                    if avg_latency < best_latency:
                        best_latency = avg_latency
                        best_provider = provider
                else:
                    # No stats yet, give it a chance
                    if best_provider is None:
                        best_provider = provider
            
            return best_provider or healthy_providers[0]
        
        # Default: return first healthy provider
        return healthy_providers[0]
    
    async def _get_fallback_provider(self, failed_provider_name: str) -> Optional[AIProvider]:
        """Get a fallback provider when one fails"""
        for provider_name, provider in self.providers.items():
            if provider_name != failed_provider_name and provider.is_healthy:
                return provider
        return None
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names"""
        return list(self.providers.keys())
    
    def get_provider(self, provider_name: str) -> Optional[AIProvider]:
        """Get specific provider by name"""
        return self.providers.get(provider_name)