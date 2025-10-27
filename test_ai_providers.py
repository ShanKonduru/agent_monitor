"""
Test script for Phase 6.1 AI Providers
Tests the AI provider system functionality
"""

import asyncio
import os
import sys
import logging

# Add project root to path
sys.path.insert(0, '.')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_ai_providers():
    """Test AI provider functionality"""
    try:
        from src.ai_providers.provider_manager import AIProviderManager
        from src.ai_providers.base_provider import AIRequest
        
        # Test configuration
        config = {
            'providers': {
                'local': {
                    'base_url': 'http://localhost:11434',
                    'provider_type': 'ollama',
                    'default_model': 'llama2'
                }
            },
            'load_balance_strategy': 'round_robin'
        }
        
        # Add OpenAI if API key available
        if os.getenv('OPENAI_API_KEY'):
            config['providers']['openai'] = {
                'api_key': os.getenv('OPENAI_API_KEY'),
                'default_model': 'gpt-3.5-turbo'
            }
            logger.info("OpenAI provider configured")
        
        # Add Anthropic if API key available
        if os.getenv('ANTHROPIC_API_KEY'):
            config['providers']['anthropic'] = {
                'api_key': os.getenv('ANTHROPIC_API_KEY'),
                'default_model': 'claude-3-haiku-20240307'
            }
            logger.info("Anthropic provider configured")
        
        # Initialize provider manager
        logger.info("Initializing AI Provider Manager...")
        provider_manager = AIProviderManager(config)
        
        # Test health checks
        logger.info("Testing provider health checks...")
        health_status = await provider_manager.health_check_all()
        logger.info(f"Health status: {health_status}")
        
        # Get available models
        logger.info("Getting available models...")
        all_models = await provider_manager.get_all_models()
        for provider_name, models in all_models.items():
            logger.info(f"{provider_name}: {len(models)} models available")
            for model in models[:2]:  # Show first 2 models
                logger.info(f"  - {model.name} ({model.description})")
        
        # Test completion with available provider
        healthy_providers = [name for name, status in health_status.items() if status]
        if healthy_providers:
            test_provider = healthy_providers[0]
            logger.info(f"Testing completion with {test_provider}...")
            
            request = AIRequest(
                prompt="Hello! Can you respond with just 'AI Provider Test Successful'?",
                max_tokens=50,
                temperature=0.1
            )
            
            try:
                response = await provider_manager.complete(request, test_provider)
                logger.info(f"✅ Completion successful!")
                logger.info(f"Response: {response.content[:100]}")
                logger.info(f"Model: {response.model}")
                logger.info(f"Tokens: {response.tokens_used}")
                logger.info(f"Latency: {response.latency_ms}ms")
                logger.info(f"Cost: ${response.cost:.4f}")
            except Exception as e:
                logger.error(f"❌ Completion failed: {e}")
        else:
            logger.warning("No healthy providers available for testing")
        
        # Get provider stats
        logger.info("Getting provider statistics...")
        stats = await provider_manager.get_provider_stats()
        for provider_name, provider_stats in stats.items():
            logger.info(f"{provider_name} stats: {provider_stats}")
        
        logger.info("✅ AI Provider test completed successfully!")
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.info("Make sure all dependencies are installed: pip install -r requirements.txt")
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("🚀 Testing Phase 6.1 AI Providers...")
    print("Note: This test requires at least one AI provider to be available:")
    print("- For OpenAI: Set OPENAI_API_KEY environment variable")
    print("- For Anthropic: Set ANTHROPIC_API_KEY environment variable") 
    print("- For Local LLM: Ensure Ollama is running on localhost:11434")
    print()
    
    asyncio.run(test_ai_providers())