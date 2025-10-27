#!/usr/bin/env python3
"""
Interactive Demo - Chatbot + MCP + PulseGuard Integration
This script demonstrates the complete integration in an interactive manner
"""

import sys
import os
import asyncio
import json
from datetime import datetime
sys.path.append('src')

# Import components
from mcp.mcp_server import MCPServer
from chatbot.chatbot_core import ChatbotCore
from ai_providers.provider_manager import AIProviderManager

class IntegratedDemo:
    def __init__(self):
        self.mcp_server = None
        self.chatbot_core = None
        self.ai_provider_manager = None
        
    async def initialize(self):
        """Initialize all components"""
        print("🚀 PULSEGUARD INTEGRATION DEMO")
        print("=" * 60)
        
        # Initialize AI Provider Manager
        print("\n🧠 1. Initializing AI Provider Manager...")
        self.ai_provider_manager = AIProviderManager()
        await self.ai_provider_manager.initialize()
        print("✅ AI Provider Manager initialized")
        
        # Show available providers
        print(f"   Available providers: {list(self.ai_provider_manager.providers.keys())}")
        
        # Initialize MCP Server
        print("\n📡 2. Initializing MCP Server...")
        self.mcp_server = MCPServer()
        await self.mcp_server.start()
        print("✅ MCP Server started")
        
        # Initialize Chatbot Core with MCP integration
        print("\n🤖 3. Initializing Chatbot Core...")
        self.chatbot_core = ChatbotCore(
            ai_provider_manager=self.ai_provider_manager,
            mcp_server=self.mcp_server
        )
        print("✅ Chatbot Core initialized with MCP integration")
        
        # Register chatbot as an MCP agent
        await self.mcp_server.register_agent(
            agent_id="demo_chatbot",
            agent_type="chatbot",
            metadata={"version": "1.0.0", "demo": True}
        )
        print("✅ Chatbot registered with MCP Server")
        
    async def demonstrate_integration(self):
        """Demonstrate the integration features"""
        print("\n" + "=" * 60)
        print("🎯 INTEGRATION DEMONSTRATION")
        print("=" * 60)
        
        # 1. Show MCP Server Status
        print("\n📊 MCP SERVER STATUS:")
        stats = await self.mcp_server.get_statistics()
        print(f"   Registered Agents: {stats['contexts']['registered_agents']}")
        print(f"   Active Contexts: {stats['contexts']['active_contexts']}")
        print(f"   Total Conversations: {stats['contexts']['total_conversations']}")
        
        # 2. Create a chat session
        print("\n💬 CREATING CHAT SESSION:")
        session = await self.chatbot_core.create_chat_session(
            user_id="demo_user",
            system_prompt="You are PulseGuard AI assistant. Help monitor and manage the agent system."
        )
        print(f"✅ Session created: {session['session_id']}")
        
        # 3. Demonstrate command processing
        print("\n🔧 TESTING CHATBOT COMMANDS:")
        
        # Test help command
        help_response = await self.chatbot_core.process_message(
            "/help",
            session['session_id']
        )
        print("✅ /help command processed")
        
        # Test status command
        status_response = await self.chatbot_core.process_message(
            "/status",
            session['session_id']
        )
        print("✅ /status command processed")
        
        # Test MCP context sharing
        share_response = await self.chatbot_core.process_message(
            "/share demo_context_integration",
            session['session_id']
        )
        print("✅ /share command processed (MCP integration)")
        
        # 4. Demonstrate AI integration
        print("\n🧠 TESTING AI INTEGRATION:")
        ai_response = await self.chatbot_core.process_message(
            "Hello! Can you help me understand how the PulseGuard system works with MCP and AI providers?",
            session['session_id']
        )
        print("✅ AI response generated")
        print(f"   Provider: {ai_response.get('provider', 'unknown')}")
        print(f"   Model: {ai_response.get('model', 'unknown')}")
        print(f"   Response preview: {ai_response.get('response', '')[:100]}...")
        
        # 5. Show MCP conversations created
        print("\n📝 MCP CONVERSATIONS:")
        conversations = await self.mcp_server.get_conversations()
        print(f"   Total conversations: {len(conversations)}")
        for i, conv in enumerate(conversations[-3:], 1):  # Show last 3
            print(f"   {i}. {conv['conversation_id']}: {len(conv['participants'])} participants")
        
        # 6. Show session statistics
        print("\n📈 SESSION STATISTICS:")
        session_stats = await self.chatbot_core.get_session_statistics(session['session_id'])
        print(f"   Total messages: {session_stats['total_messages']}")
        print(f"   Provider: {session_stats['provider']}")
        print(f"   Duration: {session_stats['duration_minutes']:.2f} minutes")
        
    async def interactive_chat(self):
        """Interactive chat demonstration"""
        print("\n" + "=" * 60)
        print("💬 INTERACTIVE CHAT DEMO")
        print("=" * 60)
        print("Type messages to chat with the AI assistant.")
        print("Commands start with '/' (e.g., /help, /status, /providers)")
        print("Type 'quit' to exit the interactive demo.")
        print("-" * 60)
        
        # Create a session for interactive demo
        session = await self.chatbot_core.create_chat_session(
            user_id="interactive_user",
            system_prompt="You are PulseGuard AI assistant. Be helpful and engaging. Mention that you're integrated with MCP server for context sharing."
        )
        
        while True:
            try:
                user_input = input("\n[YOU]: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye! Demo completed.")
                    break
                    
                if not user_input:
                    continue
                
                print("[AI]: Processing...", end="", flush=True)
                
                # Process the message
                response = await self.chatbot_core.process_message(
                    user_input,
                    session['session_id']
                )
                
                print("\r", end="")  # Clear "Processing..."
                
                if response.get('success'):
                    print(f"[AI]: {response['response']}")
                    
                    # Show additional info for commands
                    if user_input.startswith('/'):
                        print(f"      (Command: {response.get('command', 'unknown')})")
                else:
                    print(f"[AI]: Error - {response.get('error', 'Unknown error')}")
                    
            except KeyboardInterrupt:
                print("\n👋 Demo interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    async def cleanup(self):
        """Cleanup resources"""
        print("\n🧹 CLEANING UP...")
        if self.mcp_server:
            await self.mcp_server.stop()
        print("✅ Cleanup complete")

async def main():
    """Main demo function"""
    demo = IntegratedDemo()
    
    try:
        # Initialize all components
        await demo.initialize()
        
        # Run integration demonstration
        await demo.demonstrate_integration()
        
        # Ask user if they want interactive demo
        print("\n" + "=" * 60)
        choice = input("Would you like to try the interactive chat demo? (y/n): ").strip().lower()
        
        if choice in ['y', 'yes']:
            await demo.interactive_chat()
        else:
            print("✅ Demo completed!")
            
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await demo.cleanup()

if __name__ == "__main__":
    print("🎯 STARTING COMPREHENSIVE INTEGRATION DEMO")
    print("This demonstrates:")
    print("  • Phase 6.1: AI Provider Manager")
    print("  • Phase 6.2: MCP Server")
    print("  • Phase 6.3: Chatbot Interface")
    print("  • Complete PulseGuard Integration")
    print()
    
    asyncio.run(main())