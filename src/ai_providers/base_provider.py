"""
Base AI Provider Interface for Phase 6.1
Supports multiple AI providers with unified interface
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Iterator, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class ModelCapability(Enum):
    TEXT_COMPLETION = "text_completion"
    CHAT = "chat"
    CODE_GENERATION = "code_generation"
    FUNCTION_CALLING = "function_calling"
    STREAMING = "streaming"
    EMBEDDINGS = "embeddings"

@dataclass
class ModelInfo:
    """Information about an AI model"""
    name: str
    provider: str
    max_tokens: int
    capabilities: List[ModelCapability]
    cost_per_1k_tokens: float
    context_window: int
    description: str = ""
    
@dataclass
class AIRequest:
    """Standardized AI request"""
    prompt: str
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    stream: bool = False
    system_prompt: Optional[str] = None
    functions: Optional[List[Dict]] = None
    metadata: Dict[str, Any] = None
    
@dataclass
class AIResponse:
    """Standardized AI response"""
    content: str
    model: str
    provider: str
    tokens_used: int
    cost: float
    latency_ms: int
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.is_healthy = True
        self.last_health_check = datetime.now()
        
    @abstractmethod
    async def complete(self, request: AIRequest) -> AIResponse:
        """Generate text completion"""
        pass
        
    @abstractmethod
    async def stream_complete(self, request: AIRequest) -> Iterator[str]:
        """Generate streaming text completion"""
        pass
        
    @abstractmethod
    async def get_models(self) -> List[ModelInfo]:
        """Get available models from this provider"""
        pass
        
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is healthy"""
        pass
        
    async def switch_model(self, model_name: str) -> bool:
        """Switch to a different model"""
        models = await self.get_models()
        available_models = [m.name for m in models]
        
        if model_name in available_models:
            self.config['default_model'] = model_name
            return True
        return False
        
    def get_default_model(self) -> str:
        """Get the default model for this provider"""
        return self.config.get('default_model', '')
        
    def calculate_cost(self, tokens: int, model: str) -> float:
        """Calculate cost for token usage"""
        # Default implementation - providers can override
        return tokens * 0.001  # Default rate
        
    def __str__(self):
        return f"{self.__class__.__name__}({self.name})"