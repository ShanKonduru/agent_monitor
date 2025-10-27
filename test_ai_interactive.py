"""
Interactive AI Provider Testing Tool
Allows manual testing of different scenarios
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, '.')

async def interactive_test():
    """Interactive testing interface"""
    
    print("🎮 Interactive AI Provider Testing Tool")
    print("=" * 40)
    
    try:
        from src.ai_providers.provider_manager import AIProviderManager
        from src.ai_providers.base_provider import AIRequest
        
        # Setup configuration
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
        
        # Add cloud providers if available
        if os.getenv('OPENAI_API_KEY'):
            config['providers']['openai'] = {
                'api_key': os.getenv('OPENAI_API_KEY'),
                'default_model': 'gpt-3.5-turbo'
            }
            print("✅ OpenAI provider configured")
            
        if os.getenv('ANTHROPIC_API_KEY'):
            config['providers']['anthropic'] = {
                'api_key': os.getenv('ANTHROPIC_API_KEY'),
                'default_model': 'claude-3-haiku-20240307'
            }
            print("✅ Anthropic provider configured")
        
        # Initialize manager
        print("\n🚀 Initializing AI Provider Manager...")
        manager = AIProviderManager(config)
        
        # Check health
        health = await manager.health_check_all()
        healthy_providers = [name for name, status in health.items() if status]
        
        if not healthy_providers:
            print("❌ No healthy providers available!")
            return
        
        print(f"✅ Healthy providers: {healthy_providers}")
        
        while True:
            print("\n" + "="*50)
            print("🎮 INTERACTIVE AI PROVIDER TESTING")
            print("="*50)
            print("1. 🔍 Check provider health")
            print("2. 📋 List all models")
            print("3. 💬 Test completion")
            print("4. 🔄 Switch provider")
            print("5. 📊 View statistics")
            print("6. ⚡ Stream completion")
            print("7. 🎯 Benchmark latency")
            print("0. 🚪 Exit")
            
            choice = input("\n👉 Choose an option (0-7): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
                
            elif choice == "1":
                print("\n🔍 Checking provider health...")
                health = await manager.health_check_all()
                for provider, status in health.items():
                    emoji = "✅" if status else "❌"
                    print(f"{emoji} {provider}: {'Healthy' if status else 'Unhealthy'}")
                    
            elif choice == "2":
                print("\n📋 Available models:")
                models = await manager.get_all_models()
                for provider, model_list in models.items():
                    print(f"\n🏢 {provider.upper()}:")
                    for model in model_list:
                        print(f"  🤖 {model.name}")
                        print(f"     💰 ${model.cost_per_1k_tokens:.4f}/1K tokens")
                        print(f"     🧠 {model.context_window} context window")
                        
            elif choice == "3":
                print("\n💬 Testing completion...")
                prompt = input("👉 Enter your prompt: ").strip()
                if prompt:
                    provider = input(f"👉 Choose provider {healthy_providers} or press Enter for auto: ").strip()
                    provider = provider if provider in healthy_providers else None
                    
                    request = AIRequest(
                        prompt=prompt,
                        max_tokens=200,
                        temperature=0.7
                    )
                    
                    try:
                        response = await manager.complete(request, provider)
                        print(f"\n✅ Response from {response.provider} ({response.model}):")
                        print(f"💬 {response.content}")
                        print(f"📊 {response.tokens_used} tokens, {response.latency_ms}ms, ${response.cost:.4f}")
                    except Exception as e:
                        print(f"❌ Error: {e}")
                        
            elif choice == "4":
                print(f"\n🔄 Current default: {manager.default_provider}")
                new_provider = input(f"👉 Switch to {healthy_providers}: ").strip()
                if new_provider in healthy_providers:
                    success = await manager.switch_default_provider(new_provider)
                    if success:
                        print(f"✅ Switched to {new_provider}")
                    else:
                        print(f"❌ Failed to switch to {new_provider}")
                        
            elif choice == "5":
                print("\n📊 Provider statistics:")
                stats = await manager.get_provider_stats()
                for provider, provider_stats in stats.items():
                    print(f"\n🏢 {provider.upper()}:")
                    print(f"  📈 Total Requests: {provider_stats.get('requests', 0)}")
                    print(f"  ✅ Successful: {provider_stats.get('successful_requests', 0)}")
                    print(f"  ❌ Failed: {provider_stats.get('failed_requests', 0)}")
                    print(f"  📊 Success Rate: {provider_stats.get('success_rate', 0):.2%}")
                    print(f"  ⚡ Avg Latency: {provider_stats.get('avg_latency', 0):.0f}ms")
                    print(f"  🎯 Avg Tokens: {provider_stats.get('avg_tokens_per_request', 0):.1f}")
                    print(f"  💰 Total Cost: ${provider_stats.get('total_cost', 0):.4f}")
                    
            elif choice == "6":
                print("\n⚡ Testing streaming completion...")
                prompt = input("👉 Enter your prompt: ").strip()
                if prompt:
                    provider = input(f"👉 Choose provider {healthy_providers} or press Enter for auto: ").strip()
                    provider = provider if provider in healthy_providers else None
                    
                    request = AIRequest(
                        prompt=prompt,
                        max_tokens=200,
                        temperature=0.7,
                        stream=True
                    )
                    
                    try:
                        print("\n💬 Streaming response:")
                        print("=" * 40)
                        async for chunk in manager.stream_complete(request, provider):
                            print(chunk, end='', flush=True)
                        print("\n" + "=" * 40)
                        print("✅ Streaming completed")
                    except Exception as e:
                        print(f"❌ Streaming error: {e}")
                        
            elif choice == "7":
                print("\n🎯 Benchmarking latency...")
                iterations = int(input("👉 Number of requests (default 3): ").strip() or "3")
                
                for provider in healthy_providers:
                    print(f"\n🏢 Testing {provider}...")
                    latencies = []
                    
                    for i in range(iterations):
                        request = AIRequest(
                            prompt="Say 'test'",
                            max_tokens=10,
                            temperature=0
                        )
                        
                        try:
                            response = await manager.complete(request, provider)
                            latencies.append(response.latency_ms)
                            print(f"  Request {i+1}: {response.latency_ms}ms")
                        except Exception as e:
                            print(f"  Request {i+1}: Error - {e}")
                    
                    if latencies:
                        avg_latency = sum(latencies) / len(latencies)
                        min_latency = min(latencies)
                        max_latency = max(latencies)
                        print(f"  📊 Average: {avg_latency:.0f}ms")
                        print(f"  ⚡ Best: {min_latency}ms")
                        print(f"  🐌 Worst: {max_latency}ms")
            
            input("\n👉 Press Enter to continue...")
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure to run: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(interactive_test())