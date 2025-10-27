"""
Test Suite for Phase 6.2 (MCP Server) and Phase 6.3 (Chatbot)
Tests MCP server functionality and chatbot integration
"""

import asyncio
import pytest
import json
from datetime import datetime
from typing import Dict, Any

# Test imports
from src.mcp.mcp_server import MCPServer
from src.mcp.protocol import MCPMessage, MCPRequest, MessageType, AgentType
from src.chatbot.chatbot_core import ChatbotCore
from src.chatbot.chat_session import MessageType as ChatMessageType

async def test_mcp_server_basic():
    """Test basic MCP server functionality"""
    print("🧪 Testing MCP Server Basic Functionality...")
    
    # Initialize MCP server
    mcp_server = MCPServer("data/test_mcp.db")
    await mcp_server.start()
    
    try:
        # Test agent registration
        register_message = MCPRequest(
            type=MessageType.AGENT_REGISTER,
            sender_id="test_agent",
            sender_type=AgentType.EXTERNAL_CLIENT,
            payload={
                "agent_type": "chatbot",
                "name": "Test Agent",
                "capabilities": ["chat", "context_sharing"],
                "metadata": {"version": "1.0.0"}
            }
        )
        
        response = await mcp_server.process_message(register_message.to_dict())
        assert response.success, f"Agent registration failed: {response.error_message}"
        print("✅ Agent registration successful")
        
        # Test context sharing
        context_message = MCPRequest(
            type=MessageType.CONTEXT_SHARE,
            sender_id="test_agent",
            sender_type=AgentType.EXTERNAL_CLIENT,
            payload={
                "context_type": "test_context",
                "data": {"test_key": "test_value", "timestamp": datetime.now().isoformat()},
                "metadata": {"test": True},
                "expires_in_minutes": 60
            }
        )
        
        response = await mcp_server.process_message(context_message.to_dict())
        assert response.success, f"Context sharing failed: {response.error_message}"
        context_id = response.response_data.get("context_id")
        print(f"✅ Context sharing successful: {context_id}")
        
        # Test conversation start
        conversation_message = MCPRequest(
            type=MessageType.CONVERSATION_START,
            sender_id="test_agent",
            sender_type=AgentType.EXTERNAL_CLIENT,
            payload={
                "title": "Test Conversation",
                "participants": ["test_agent", "user_1"],
                "metadata": {"test_conversation": True}
            }
        )
        
        response = await mcp_server.process_message(conversation_message.to_dict())
        assert response.success, f"Conversation start failed: {response.error_message}"
        conversation_id = response.response_data.get("conversation_id")
        print(f"✅ Conversation start successful: {conversation_id}")
        
        # Test memory storage and retrieval
        memory_store_message = MCPRequest(
            type=MessageType.MEMORY_STORE,
            sender_id="test_agent",
            sender_type=AgentType.EXTERNAL_CLIENT,
            payload={
                "memory_type": "agent_state",
                "data": {"current_state": "active", "last_action": "test"},
                "metadata": {"agent_id": "test_agent"}
            }
        )
        
        response = await mcp_server.process_message(memory_store_message.to_dict())
        assert response.success, f"Memory storage failed: {response.error_message}"
        memory_context_id = response.response_data.get("context_id")
        print(f"✅ Memory storage successful: {memory_context_id}")
        
        # Test memory retrieval
        memory_retrieve_message = MCPRequest(
            type=MessageType.MEMORY_RETRIEVE,
            sender_id="test_agent",
            sender_type=AgentType.EXTERNAL_CLIENT,
            payload={"context_id": memory_context_id}
        )
        
        response = await mcp_server.process_message(memory_retrieve_message.to_dict())
        assert response.success, f"Memory retrieval failed: {response.error_message}"
        retrieved_context = response.response_data.get("context")
        assert retrieved_context is not None, "No context retrieved"
        print(f"✅ Memory retrieval successful: {retrieved_context['data']}")
        
        # Get statistics
        stats = mcp_server.get_statistics()
        print(f"📊 MCP Server Statistics: {json.dumps(stats, indent=2)}")
        
        return True
        
    finally:
        await mcp_server.stop()

async def test_chatbot_core_basic():
    """Test basic chatbot functionality"""
    print("\n🤖 Testing Chatbot Core Basic Functionality...")
    
    # Initialize chatbot (without real providers for testing)
    chatbot = ChatbotCore(ai_provider_manager=None, mcp_server=None)
    
    # Create a chat session
    session = await chatbot.create_chat_session(
        user_id="test_user",
        title="Test Chat Session",
        ai_provider="local",
        ai_model="llama3.1",
        system_prompt="friendly"
    )
    
    print(f"✅ Chat session created: {session.session_id}")
    
    # Test command processing
    command_result = await chatbot.process_message(
        session.session_id,
        "/help"
    )
    
    assert command_result["success"], f"Command processing failed: {command_result.get('error')}"
    assert command_result["type"] == "command", "Expected command response"
    print("✅ Command processing successful")
    print(f"💬 Help response: {command_result['response'][:100]}...")
    
    # Test another command
    status_result = await chatbot.process_message(
        session.session_id,
        "/status"
    )
    
    assert status_result["success"], f"Status command failed: {status_result.get('error')}"
    print("✅ Status command successful")
    
    # Test provider command
    provider_result = await chatbot.process_message(
        session.session_id,
        "/providers"
    )
    
    assert provider_result["success"], f"Providers command failed: {provider_result.get('error')}"
    print("✅ Providers command successful")
    
    # Test chat message (will use mock AI integration)
    chat_result = await chatbot.process_message(
        session.session_id,
        "Hello, can you help me with the Agent Monitor system?"
    )
    
    assert chat_result["success"], f"Chat message failed: {chat_result.get('error')}"
    assert chat_result["type"] == "chat", "Expected chat response"
    print("✅ Chat message processing successful")
    print(f"🤖 AI Response: {chat_result['response'][:100]}...")
    
    # Get session statistics
    session_stats = session.calculate_statistics()
    print(f"📊 Session Statistics: {json.dumps(session_stats, indent=2)}")
    
    # Get chatbot statistics
    chatbot_stats = chatbot.get_statistics()
    print(f"📊 Chatbot Statistics: {json.dumps(chatbot_stats, indent=2)}")
    
    return True

async def test_mcp_chatbot_integration():
    """Test MCP server and chatbot integration"""
    print("\n🔗 Testing MCP-Chatbot Integration...")
    
    # Initialize MCP server
    mcp_server = MCPServer("data/test_integration_mcp.db")
    await mcp_server.start()
    
    # Initialize chatbot with MCP server
    chatbot = ChatbotCore(ai_provider_manager=None, mcp_server=mcp_server)
    
    try:
        # Create chat session (should create MCP conversation)
        session = await chatbot.create_chat_session(
            user_id="integration_user",
            title="Integration Test Chat",
            ai_provider="local",
            ai_model="llama3.1"
        )
        
        print(f"✅ Integrated session created: {session.session_id}")
        print(f"🔗 MCP Conversation ID: {session.mcp_conversation_id}")
        
        # Send a message (should be added to MCP conversation)
        result = await chatbot.process_message(
            session.session_id,
            "Test message for MCP integration"
        )
        
        assert result["success"], f"Integration message failed: {result.get('error')}"
        print("✅ Message with MCP integration successful")
        
        # Test context sharing command
        context_result = await chatbot.process_message(
            session.session_id,
            "/share test_context"
        )
        
        assert context_result["success"], f"Context sharing failed: {context_result.get('error')}"
        print("✅ Context sharing through chatbot successful")
        
        # Get MCP conversations
        conversations = mcp_server.get_conversations()
        print(f"📊 MCP Conversations: {len(conversations)} found")
        
        # Get MCP contexts
        contexts = mcp_server.get_contexts("conversation")
        print(f"📊 MCP Contexts: {len(contexts)} conversation contexts found")
        
        return True
        
    finally:
        await mcp_server.stop()

async def test_chatbot_commands():
    """Test various chatbot commands"""
    print("\n⚡ Testing Chatbot Commands...")
    
    chatbot = ChatbotCore(ai_provider_manager=None, mcp_server=None)
    session = await chatbot.create_chat_session(user_id="command_test_user")
    
    commands_to_test = [
        "/help",
        "/help provider",
        "/status",
        "/stats", 
        "/providers",
        "/models",
        "/context",
        "/clear",
        "/debug on",
        "/test"
    ]
    
    results = {}
    
    for command in commands_to_test:
        try:
            result = await chatbot.process_message(session.session_id, command)
            results[command] = {
                "success": result["success"],
                "response_length": len(result.get("response", "")),
                "type": result.get("type")
            }
            status = "✅" if result["success"] else "❌"
            print(f"{status} {command}: {result.get('response', 'No response')[:50]}...")
        except Exception as e:
            results[command] = {"success": False, "error": str(e)}
            print(f"❌ {command}: Error - {e}")
    
    # Summary
    successful_commands = sum(1 for r in results.values() if r.get("success"))
    total_commands = len(commands_to_test)
    print(f"\n📊 Command Test Summary: {successful_commands}/{total_commands} successful")
    
    return successful_commands > 0

async def run_comprehensive_test():
    """Run comprehensive test suite"""
    print("🚀 PHASE 6.2 & 6.3 COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    test_results = {}
    
    try:
        # Test 1: MCP Server Basic
        print("\n" + "=" * 40)
        test_results["mcp_basic"] = await test_mcp_server_basic()
        
        # Test 2: Chatbot Core Basic
        print("\n" + "=" * 40)
        test_results["chatbot_basic"] = await test_chatbot_core_basic()
        
        # Test 3: MCP-Chatbot Integration
        print("\n" + "=" * 40)
        test_results["integration"] = await test_mcp_chatbot_integration()
        
        # Test 4: Chatbot Commands
        print("\n" + "=" * 40)
        test_results["commands"] = await test_chatbot_commands()
        
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        test_results["error"] = str(e)
    
    # Final Summary
    print("\n" + "=" * 60)
    print("🎯 FINAL TEST RESULTS")
    print("=" * 60)
    
    for test_name, result in test_results.items():
        if isinstance(result, bool):
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
        else:
            print(f"{test_name}: ❌ ERROR - {result}")
    
    passed_tests = sum(1 for r in test_results.values() if r is True)
    total_tests = len([r for r in test_results.values() if isinstance(r, bool)])
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Phase 6.2 & 6.3 implementations are working!")
    elif passed_tests > 0:
        print("⚠️  Some tests passed. Partial functionality working.")
    else:
        print("❌ All tests failed. Implementation needs review.")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())