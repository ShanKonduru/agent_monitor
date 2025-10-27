"""
AI Providers API Router for Phase 6.1
FastAPI endpoints for AI provider management and interoperability
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import logging

from ..ai_providers.provider_manager import AIProviderManager
from ..ai_providers.base_provider import AIRequest, AIResponse, ModelInfo

logger = logging.getLogger(__name__)

# Global provider manager instance
provider_manager = None

class AICompletionRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    provider: Optional[str] = None
    max_tokens: Optional[int] = 1000
    temperature: float = 0.7
    stream: bool = False
    system_prompt: Optional[str] = None

class ProviderSwitchRequest(BaseModel):
    provider_name: str

class ModelSwitchRequest(BaseModel):
    provider_name: str
    model_name: str

# Create router
router = APIRouter(prefix="/api/v1/ai", tags=["AI Providers"])

def get_provider_manager() -> AIProviderManager:
    """Dependency to get provider manager"""
    global provider_manager
    if not provider_manager:
        raise HTTPException(status_code=503, detail="AI Provider Manager not initialized")
    return provider_manager

def set_provider_manager(pm: AIProviderManager):
    """Set the global provider manager"""
    global provider_manager
    provider_manager = pm

@router.get("/providers")
async def get_available_providers(pm: AIProviderManager = Depends(get_provider_manager)):
    """Get list of available AI providers"""
    try:
        providers = pm.get_available_providers()
        health_status = await pm.health_check_all()
        
        return {
            "providers": providers,
            "health_status": health_status,
            "default_provider": pm.default_provider
        }
    except Exception as e:
        logger.error(f"Failed to get providers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def get_all_models(pm: AIProviderManager = Depends(get_provider_manager)):
    """Get all available models from all providers"""
    try:
        models = await pm.get_all_models()
        return {"models": models}
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/{provider_name}")
async def get_provider_models(provider_name: str, pm: AIProviderManager = Depends(get_provider_manager)):
    """Get models for a specific provider"""
    try:
        provider = pm.get_provider(provider_name)
        if not provider:
            raise HTTPException(status_code=404, detail=f"Provider {provider_name} not found")
        
        models = await provider.get_models()
        return {"provider": provider_name, "models": models}
    except Exception as e:
        logger.error(f"Failed to get models for {provider_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/complete")
async def complete_request(
    request: AICompletionRequest, 
    pm: AIProviderManager = Depends(get_provider_manager)
):
    """Generate AI completion using specified or default provider"""
    try:
        # Convert to internal request format
        ai_request = AIRequest(
            prompt=request.prompt,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=request.stream,
            system_prompt=request.system_prompt
        )
        
        # Get completion
        response = await pm.complete(ai_request, request.provider)
        
        return {
            "content": response.content,
            "model": response.model,
            "provider": response.provider,
            "tokens_used": response.tokens_used,
            "cost": response.cost,
            "latency_ms": response.latency_ms,
            "timestamp": response.timestamp.isoformat(),
            "metadata": response.metadata
        }
    except Exception as e:
        logger.error(f"AI completion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/switch-provider")
async def switch_default_provider(
    request: ProviderSwitchRequest,
    pm: AIProviderManager = Depends(get_provider_manager)
):
    """Switch the default AI provider"""
    try:
        success = await pm.switch_default_provider(request.provider_name)
        if success:
            return {
                "message": f"Default provider switched to {request.provider_name}",
                "new_default": request.provider_name
            }
        else:
            raise HTTPException(status_code=404, detail=f"Provider {request.provider_name} not found")
    except Exception as e:
        logger.error(f"Failed to switch provider: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/switch-model")
async def switch_provider_model(
    request: ModelSwitchRequest,
    pm: AIProviderManager = Depends(get_provider_manager)
):
    """Switch model for a specific provider"""
    try:
        provider = pm.get_provider(request.provider_name)
        if not provider:
            raise HTTPException(status_code=404, detail=f"Provider {request.provider_name} not found")
        
        success = await provider.switch_model(request.model_name)
        if success:
            return {
                "message": f"Model switched to {request.model_name} for provider {request.provider_name}",
                "provider": request.provider_name,
                "new_model": request.model_name
            }
        else:
            raise HTTPException(status_code=404, detail=f"Model {request.model_name} not available for provider {request.provider_name}")
    except Exception as e:
        logger.error(f"Failed to switch model: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def check_providers_health(pm: AIProviderManager = Depends(get_provider_manager)):
    """Check health status of all AI providers"""
    try:
        health_status = await pm.health_check_all()
        return {
            "health_status": health_status,
            "last_check": pm.last_health_check.isoformat(),
            "healthy_providers": [name for name, status in health_status.items() if status],
            "unhealthy_providers": [name for name, status in health_status.items() if not status]
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_provider_statistics(pm: AIProviderManager = Depends(get_provider_manager)):
    """Get performance statistics for all AI providers"""
    try:
        stats = await pm.get_provider_stats()
        return {"statistics": stats}
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/config")
async def get_provider_configuration(pm: AIProviderManager = Depends(get_provider_manager)):
    """Get current AI provider configuration"""
    try:
        return {
            "available_providers": pm.get_available_providers(),
            "default_provider": pm.default_provider,
            "load_balance_strategy": pm.load_balance_strategy,
            "health_check_interval": pm.health_check_interval
        }
    except Exception as e:
        logger.error(f"Failed to get config: {e}")
        raise HTTPException(status_code=500, detail=str(e))