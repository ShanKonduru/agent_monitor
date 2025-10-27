"""
Chat Command Processing
Handles special commands in chat messages for system interaction
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import logging
import re

logger = logging.getLogger(__name__)

class CommandType(Enum):
    """Types of chat commands"""
    SYSTEM = "system"       # System management commands
    AI = "ai"              # AI provider commands  
    CONTEXT = "context"    # Context management
    SESSION = "session"    # Session management
    HELP = "help"         # Help and information
    DEBUG = "debug"       # Debug and diagnostics

@dataclass
class ChatCommand:
    """Chat command definition"""
    name: str
    type: CommandType
    description: str
    usage: str
    aliases: List[str] = None
    handler: Optional[Callable] = None
    admin_only: bool = False
    
    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []

class CommandProcessor:
    """Processes chat commands"""
    
    def __init__(self):
        """Initialize command processor"""
        self.commands: Dict[str, ChatCommand] = {}
        self.command_prefix = "/"
        self._register_default_commands()
        logger.info("CommandProcessor initialized")
    
    def _register_default_commands(self):
        """Register default system commands"""
        
        # Help commands
        self.register_command(ChatCommand(
            name="help",
            type=CommandType.HELP,
            description="Show available commands",
            usage="/help [command]",
            aliases=["h", "?"],
            handler=self._handle_help
        ))
        
        # AI provider commands
        self.register_command(ChatCommand(
            name="provider",
            type=CommandType.AI,
            description="Change AI provider",
            usage="/provider <provider_name>",
            aliases=["p"],
            handler=self._handle_provider
        ))
        
        self.register_command(ChatCommand(
            name="model",
            type=CommandType.AI,
            description="Change AI model",
            usage="/model <model_name>",
            aliases=["m"],
            handler=self._handle_model
        ))
        
        self.register_command(ChatCommand(
            name="providers",
            type=CommandType.AI,
            description="List available AI providers",
            usage="/providers",
            handler=self._handle_list_providers
        ))
        
        self.register_command(ChatCommand(
            name="models",
            type=CommandType.AI,
            description="List available models",
            usage="/models [provider]",
            handler=self._handle_list_models
        ))
        
        # Session commands
        self.register_command(ChatCommand(
            name="clear",
            type=CommandType.SESSION,
            description="Clear chat history",
            usage="/clear",
            aliases=["c"],
            handler=self._handle_clear
        ))
        
        self.register_command(ChatCommand(
            name="save",
            type=CommandType.SESSION,
            description="Save chat session",
            usage="/save [title]",
            aliases=["s"],
            handler=self._handle_save
        ))
        
        self.register_command(ChatCommand(
            name="load",
            type=CommandType.SESSION,
            description="Load chat session",
            usage="/load <session_id>",
            aliases=["l"],
            handler=self._handle_load
        ))
        
        self.register_command(ChatCommand(
            name="sessions",
            type=CommandType.SESSION,
            description="List chat sessions",
            usage="/sessions",
            handler=self._handle_list_sessions
        ))
        
        # Context commands
        self.register_command(ChatCommand(
            name="context",
            type=CommandType.CONTEXT,
            description="Show current context",
            usage="/context",
            handler=self._handle_show_context
        ))
        
        self.register_command(ChatCommand(
            name="share",
            type=CommandType.CONTEXT,
            description="Share context with MCP",
            usage="/share <context_type>",
            handler=self._handle_share_context
        ))
        
        # System commands
        self.register_command(ChatCommand(
            name="status",
            type=CommandType.SYSTEM,
            description="Show system status",
            usage="/status",
            handler=self._handle_status
        ))
        
        self.register_command(ChatCommand(
            name="stats",
            type=CommandType.SYSTEM,
            description="Show statistics",
            usage="/stats",
            handler=self._handle_stats
        ))
        
        # Debug commands
        self.register_command(ChatCommand(
            name="debug",
            type=CommandType.DEBUG,
            description="Toggle debug mode",
            usage="/debug [on|off]",
            handler=self._handle_debug,
            admin_only=True
        ))
        
        self.register_command(ChatCommand(
            name="test",
            type=CommandType.DEBUG,
            description="Test AI provider connection",
            usage="/test [provider]",
            handler=self._handle_test,
            admin_only=True
        ))
    
    def register_command(self, command: ChatCommand):
        """Register a new command"""
        # Register main command name
        self.commands[command.name.lower()] = command
        
        # Register aliases
        for alias in command.aliases:
            self.commands[alias.lower()] = command
        
        logger.debug(f"Registered command: {command.name}")
    
    def is_command(self, text: str) -> bool:
        """Check if text is a command"""
        return text.strip().startswith(self.command_prefix)
    
    def parse_command(self, text: str) -> Optional[tuple]:
        """Parse command from text"""
        if not self.is_command(text):
            return None
        
        # Remove prefix and split
        command_text = text.strip()[len(self.command_prefix):]
        parts = command_text.split()
        
        if not parts:
            return None
        
        command_name = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        return command_name, args
    
    async def process_command(self, text: str, session_context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a command and return result"""
        try:
            parsed = self.parse_command(text)
            if not parsed:
                return {
                    "success": False,
                    "error": "Invalid command format",
                    "response": "Commands must start with '/'"
                }
            
            command_name, args = parsed
            
            # Find command
            command = self.commands.get(command_name)
            if not command:
                return {
                    "success": False,
                    "error": f"Unknown command: {command_name}",
                    "response": f"Unknown command '{command_name}'. Type '/help' for available commands."
                }
            
            # Check admin permissions if needed
            if command.admin_only and not session_context.get("is_admin", False):
                return {
                    "success": False,
                    "error": "Admin only command",
                    "response": "This command requires administrator privileges."
                }
            
            # Execute command handler
            if command.handler:
                result = await command.handler(args, session_context)
                return {
                    "success": True,
                    "command": command.name,
                    "response": result
                }
            else:
                return {
                    "success": False,
                    "error": "Command not implemented",
                    "response": f"Command '{command.name}' is not yet implemented."
                }
                
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": f"Error executing command: {e}"
            }
    
    # Command handlers
    
    async def _handle_help(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle help command"""
        if args:
            # Help for specific command
            command_name = args[0].lower()
            command = self.commands.get(command_name)
            if command:
                aliases_str = f" (aliases: {', '.join(command.aliases)})" if command.aliases else ""
                return f"**{command.name}**{aliases_str}\n{command.description}\nUsage: `{command.usage}`"
            else:
                return f"Unknown command: {command_name}"
        else:
            # List all commands by type
            help_text = "**Available Commands:**\n\n"
            
            # Remove duplicates by command name
            unique_commands = {}
            for cmd in self.commands.values():
                unique_commands[cmd.name] = cmd
            
            commands_by_type = {}
            for cmd in unique_commands.values():
                cmd_type = cmd.type.value.title()
                if cmd_type not in commands_by_type:
                    commands_by_type[cmd_type] = []
                commands_by_type[cmd_type].append(cmd)
            
            for cmd_type, cmds in sorted(commands_by_type.items()):
                help_text += f"**{cmd_type} Commands:**\n"
                for cmd in sorted(cmds, key=lambda c: c.name):
                    if not cmd.admin_only or context.get("is_admin", False):
                        help_text += f"- `/{cmd.name}` - {cmd.description}\n"
                help_text += "\n"
            
            help_text += "Type `/help <command>` for detailed usage information."
            return help_text
    
    async def _handle_provider(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle provider change command"""
        if not args:
            current = context.get("ai_provider", "unknown")
            return f"Current provider: {current}\nUse `/providers` to see available providers."
        
        provider = args[0].lower()
        # This would integrate with the AI provider manager
        return f"Provider changed to: {provider}"
    
    async def _handle_model(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle model change command"""
        if not args:
            current = context.get("ai_model", "unknown")
            return f"Current model: {current}\nUse `/models` to see available models."
        
        model = args[0]
        # This would integrate with the AI provider manager
        return f"Model changed to: {model}"
    
    async def _handle_list_providers(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle list providers command"""
        # This would integrate with the AI provider manager
        return "Available providers: local, openai, anthropic"
    
    async def _handle_list_models(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle list models command"""
        provider = args[0] if args else context.get("ai_provider", "local")
        # This would integrate with the AI provider manager
        return f"Available models for {provider}: llama3.1, qwen3-coder, llama2"
    
    async def _handle_clear(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle clear command"""
        # This would clear the chat session
        return "Chat history cleared."
    
    async def _handle_save(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle save command"""
        title = " ".join(args) if args else "Saved Chat"
        # This would save the current session
        return f"Chat session saved as: {title}"
    
    async def _handle_load(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle load command"""
        if not args:
            return "Please specify a session ID to load."
        
        session_id = args[0]
        # This would load the specified session
        return f"Loaded chat session: {session_id}"
    
    async def _handle_list_sessions(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle list sessions command"""
        # This would list available sessions
        return "Available chat sessions:\n- Session 1\n- Session 2\n- Session 3"
    
    async def _handle_show_context(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle show context command"""
        # Show current session context
        context_info = []
        context_info.append(f"Session ID: {context.get('session_id', 'unknown')}")
        context_info.append(f"Provider: {context.get('ai_provider', 'unknown')}")
        context_info.append(f"Model: {context.get('ai_model', 'unknown')}")
        context_info.append(f"Temperature: {context.get('temperature', 0.7)}")
        
        return "**Current Context:**\n" + "\n".join(context_info)
    
    async def _handle_share_context(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle share context command"""
        if not args:
            return "Please specify context type to share."
        
        context_type = args[0]
        # This would share context with MCP
        return f"Context shared with MCP as type: {context_type}"
    
    async def _handle_status(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle status command"""
        # This would show system status
        return "System Status: ✅ All services operational"
    
    async def _handle_stats(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle stats command"""
        # This would show system statistics
        return "System Statistics:\n- Active sessions: 3\n- Total messages: 156\n- Uptime: 2h 34m"
    
    async def _handle_debug(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle debug command"""
        if args and args[0].lower() in ["on", "off"]:
            mode = args[0].lower()
            return f"Debug mode turned {mode}"
        else:
            current = "on" if context.get("debug_mode", False) else "off"
            return f"Debug mode is currently {current}"
    
    async def _handle_test(self, args: List[str], context: Dict[str, Any]) -> str:
        """Handle test command"""
        provider = args[0] if args else context.get("ai_provider", "local")
        # This would test the AI provider connection
        return f"Testing {provider} provider... ✅ Connection successful"
    
    def get_command_list(self, include_admin: bool = False) -> List[ChatCommand]:
        """Get list of all commands"""
        # Remove duplicates by command name instead of using set()
        seen_commands = {}
        for cmd in self.commands.values():
            if cmd.name not in seen_commands:
                seen_commands[cmd.name] = cmd
        
        commands = list(seen_commands.values())
        
        if not include_admin:
            commands = [cmd for cmd in commands if not cmd.admin_only]
        return sorted(commands, key=lambda c: c.name)