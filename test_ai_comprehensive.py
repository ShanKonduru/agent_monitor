"""
Comprehensive Test Suite for Phase 6.1 AI Providers
Multiple test scenarios and provider configurations
"""

import asyncio
import os
import sys
import logging
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, '.')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_provider_health():
    """Test all provider health checks"""
    print("🔍 Testing Provider Health Checks...")
    
    try:
        from src.ai_providers.provider_manager import AIProviderManager
        
        config = {
            'providers': {
                'local': {
                    'base_url': 'http://localhost:11434',
                    'provider_type': 'ollama',
                    'default_model': 'llama2'
                }
            }
        }
        
        # Add cloud providers if API keys available
        if os.getenv('OPENAI_API_KEY'):
            config['providers']['openai'] = {
                'api_key': os.getenv('OPENAI_API_KEY'),
                'default_model': 'gpt-3.5-turbo'
            }
            
        if os.getenv('ANTHROPIC_API_KEY'):
            config['providers']['anthropic'] = {
                'api_key': os.getenv('ANTHROPIC_API_KEY'),
                'default_model': 'claude-3-haiku-20240307'
            }
        
        manager = AIProviderManager(config)
        health = await manager.health_check_all()
        
        print(f"✅ Health Check Results: {health}")
        return health
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return {}

async def test_model_listing():
    """Test getting models from all providers"""
    print("📋 Testing Model Listing...")
    
    try:
        from src.ai_providers.provider_manager import AIProviderManager
        
        config = {
            'providers': {
                'local': {
                    'base_url': 'http://localhost:11434',
                    'provider_type': 'ollama',
                    'default_model': 'llama2'
                }
            }
        }
        
        manager = AIProviderManager(config)
        models = await manager.get_all_models()
        
        for provider, model_list in models.items():
            print(f"📦 {provider}: {len(model_list)} models")
            for model in model_list[:3]:  # Show first 3
                print(f"  🤖 {model.name} - {model.description}")
                print(f"     💰 ${model.cost_per_1k_tokens:.4f}/1K tokens")
                print(f"     🧠 {model.context_window} context window")
        
        return models
        
    except Exception as e:
        print(f"❌ Model listing failed: {e}")
        return {}

async def test_completions():
    """Test AI completions with different prompts"""
    print("💬 Testing AI Completions...")
    
    try:
        from src.ai_providers.provider_manager import AIProviderManager
        from src.ai_providers.base_provider import AIRequest
        
        config = {
            'providers': {
                'local': {
                    'base_url': 'http://localhost:11434',
                    'provider_type': 'ollama',
                    'default_model': 'llama2'
                }
            }
        }
        
        manager = AIProviderManager(config)
        
        test_prompts = [
            "What is 2+2?",
            "Write a haiku about AI",
            "Explain Python in one sentence"
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n🔤 Test {i}: {prompt}")
            
            request = AIRequest(
                prompt=prompt,
                max_tokens=100,
                temperature=0.7
            )
            
            try:
                response = await manager.complete(request)
                print(f"✅ Response: {response.content[:100]}...")
                print(f"📊 Stats: {response.tokens_used} tokens, {response.latency_ms}ms, ${response.cost:.4f}")
            except Exception as e:
                print(f"❌ Completion failed: {e}")
        
        # Get final stats
        stats = await manager.get_provider_stats()
        print(f"\n📈 Final Statistics: {json.dumps(stats, indent=2)}")
        
    except Exception as e:
        print(f"❌ Completion testing failed: {e}")

async def test_provider_switching():
    """Test switching between providers"""
    print("🔄 Testing Provider Switching...")
    
    try:
        from src.ai_providers.provider_manager import AIProviderManager
        
        config = {
            'providers': {
                'local': {
                    'base_url': 'http://localhost:11434',
                    'provider_type': 'ollama',
                    'default_model': 'llama2'
                }
            }
        }
        
        # Add multiple providers if available
        if os.getenv('OPENAI_API_KEY'):
            config['providers']['openai'] = {
                'api_key': os.getenv('OPENAI_API_KEY'),
                'default_model': 'gpt-3.5-turbo'
            }
        
        manager = AIProviderManager(config)
        
        print(f"🏠 Default provider: {manager.default_provider}")
        
        # Test switching
        for provider in manager.get_available_providers():
            success = await manager.switch_default_provider(provider)
            print(f"🔄 Switch to {provider}: {'✅' if success else '❌'}")
            print(f"🏠 Current default: {manager.default_provider}")
        
    except Exception as e:
        print(f"❌ Provider switching test failed: {e}")

async def run_comprehensive_test():
    """Run all tests"""
    print("🚀 COMPREHENSIVE AI PROVIDER TEST SUITE")
    print("=" * 50)
    
    # Test 1: Health checks
    health = await test_provider_health()
    healthy_providers = [name for name, status in health.items() if status]
    
    if not healthy_providers:
        print("❌ No healthy providers available. Please check:")
        print("  - Ollama running on localhost:11434")
        print("  - OPENAI_API_KEY environment variable")
        print("  - ANTHROPIC_API_KEY environment variable")
        return
    
    print(f"✅ {len(healthy_providers)} healthy providers: {healthy_providers}")
    
    # Test 2: Model listing
    await test_model_listing()
    
    # Test 3: Completions
    await test_completions()
    
    # Test 4: Provider switching
    await test_provider_switching()
    
    print("\n🎉 ALL TESTS COMPLETED!")

if __name__ == "__main__":
    print("🧪 Phase 6.1 AI Provider Comprehensive Test Suite")
    print("This will test all aspects of the AI provider system\n")
    
    asyncio.run(run_comprehensive_test())