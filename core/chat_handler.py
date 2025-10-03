"""
Chat Handler Module

This module provides a ChatHandler class that integrates Google's Gemini AI model
with Model Context Protocol (MCP) tools. It enables conversational AI with
function calling capabilities through MCP servers.

Key Features:
- Integration with Google Gemini AI models
- MCP tool discovery and execution
- Chat history management
- Synchronous and asynchronous tool calling
- Multi-turn conversation handling with tool chaining
"""

# Google Gemini AI imports
from google.genai import Client as GeminiClient
from google.genai.types import GenerateContentConfig, Tool, Part, FunctionDeclaration
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Model Context Protocol (MCP) imports
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters
import asyncio

class ChatHandler:
    """
    A chat handler that integrates Google Gemini AI with MCP (Model Context Protocol) tools.
    
    This class manages conversations with the Gemini AI model while providing access
    to external tools through MCP servers. It handles tool discovery, execution,
    and maintains chat history.
    
    Attributes:
        gemini_model (str): The Gemini model to use for chat
        api_key (str): Google Gemini API key
        save_history_enabled (bool): Whether to save chat history to files
        chat_history (str): Path to the chat history file
        system_instruction (str): System instructions for the AI model
        available_tools (list): List of available MCP tool names
        chat_tools (Tool): Gemini Tool object containing function declarations
        client (GeminiClient): Google Gemini client instance
        chat_session: Active chat session with Gemini
    """
    
    def __init__(self, system_instructions: str = "",  approval_callback=None):
        """
        Initialize the chat handler with tools and chat session.
                   
        Raises:
            ValueError: If GEMINI_API_KEY is not set in environment variables
        """
        # Load environment variables from .env file if present
        load_dotenv()
        try:
            with open("data/system_instruction.txt", "r", encoding="utf-8") as f:
                system_instructions = f.read()
        except FileNotFoundError:
            system_instructions = """You are an exceptionally helpful and friendly chatbot. 
            Your purpose is to provide concise and accurate information as requested by the user. 
            If a question is outside of your capabilities, politely inform the user that you are unable to help with that request.
            """
        # Configure Gemini model and API key
        self.gemini_model = os.environ.get("GEMINI_MODEL")
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set in .env file or environment variables.")
        
        # Set up chat history management
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # Create unique timestamp for history file
        self.save_history_enabled = os.getenv("GEMINI_SAVE_CHAT_HISTORY", "false").lower() in ("true", "1", "yes")
        self.chat_history = f"data/chat_history{timestamp}.json"  # Unique filename per session
        
        # Set up the system instructions
        self.system_instruction = system_instructions
        
        # Discover and configure MCP tools
        self.available_tools, function_declarations, self.sensitive_tools = self._get_mcp_tools()
        self.chat_tools = Tool(function_declarations=function_declarations)
        
        # Initialize Gemini client and create chat session
        self.client = GeminiClient(api_key=self.api_key)
        self.chat_session = self.client.chats.create(
            model=self.gemini_model,
            config=GenerateContentConfig(
                temperature=0,  # Deterministic responses
                system_instruction=self.system_instruction,
                tools=[self.chat_tools]  # Enable function calling
            ),
            history=[]  # Start with empty conversation history
        )
        # Store approval callback
        self.approval_callback = approval_callback
        self.pending_tools = [] 

    def _get_mcp_tools(self):
        """
        Synchronously retrieve tool definitions from MCP server.
        
        This method connects to the MCP server, discovers available tools,
        and converts them into Gemini-compatible function declarations.
        
        Returns:
            tuple: A tuple containing:
                - available_tools (list): List of tool names
                - all_tools_dec (list): List of FunctionDeclaration objects for Gemini
        """
        async def _fetch_tools():
            """Internal async function to fetch tools from MCP server."""
            # Configure MCP server connection parameters
            server_params = StdioServerParameters(
                command="python",
                args=["mcp_server.py"],
            )
            
            # Connect to MCP server and discover tools
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the MCP session
                    await session.initialize()
                    
                    # Get list of available tools from MCP server
                    mcp_tools = await session.list_tools()
                    
                    # Extract tool names for validation
                    available_tools = [tool.name for tool in mcp_tools.tools]
                    
                    # Convert MCP tools to Gemini function declarations
                    all_tools_dec = []
                    sensitive_tools = set()
                    for tool in mcp_tools.tools:
                        # Clean up the input schema by removing MCP-specific properties
                        params = {
                            k: v
                            for k, v in tool.inputSchema.items()
                            if k not in ["additionalProperties", "$schema"]
                        }
                        
                        # Track sensitive tool names based on description marker
                        if "[USER-APPROVAL-REQUIRED]" in (tool.description or ""):
                            sensitive_tools.add(tool.name)

                        # Create Gemini-compatible function declaration
                        all_tools_dec.append(
                            FunctionDeclaration(
                                name=tool.name,
                                description=tool.description,
                                parameters=params
                            )
                        )
                    
                    return available_tools, all_tools_dec, sensitive_tools

        # Run the async function synchronously
        return asyncio.run(_fetch_tools())

    async def call_tool_async(self, tool_name: str, **kwargs):
        """
        Asynchronously call a tool via MCP stdio client.
        
        This method establishes a connection to the MCP server and executes
        the specified tool with the provided arguments.
        
        Args:
            tool_name (str): Name of the tool to call
            **kwargs: Arguments to pass to the tool
            
        Returns:
            The result from the tool execution
            
        Raises:
            ValueError: If the tool name is not found in available tools
        """
        # Configure MCP server connection parameters
        server_params = StdioServerParameters(
            command="python",
            args=["mcp_server.py"]
        )
        
        # Connect to MCP server and execute tool
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the MCP session
                await session.initialize()
               
                # Validate tool exists
                if tool_name not in self.available_tools:
                    raise ValueError(f"Tool '{tool_name}' not found. Available tools: {self.available_tools}")
                
                # Execute the tool with provided arguments
                result = await session.call_tool(tool_name, arguments=kwargs)
                return result

    def call_tool_sync(self, tool_name: str, **kwargs):
        """
        Synchronous wrapper for calling an MCP tool.
        
        This method provides a synchronous interface to the async tool calling
        functionality, making it easier to use in synchronous contexts.
        
        Args:
            tool_name (str): Name of the tool to call
            **kwargs: Arguments to pass to the tool
            
        Returns:
            The result from the tool execution
        """
        return asyncio.run(self.call_tool_async(tool_name, **kwargs))

    def request_user_approval(self, tool_name: str, tool_args: dict) -> bool:
        """
        Request user approval before executing a sensitive tool.
        
        Args:
            tool_name (str): The name of the tool requiring approval
            tool_args (dict): The arguments the tool will be called with
        
        Returns:
            bool: True if user approves, False otherwise
        """
        if self.approval_callback:
            return self.approval_callback(tool_name, tool_args)
            
        print(f"\n⚠️ The tool '{tool_name}' requires approval before execution.")
        print(f"Arguments: {json.dumps(tool_args, indent=2)}")
        choice = input("Do you want to proceed? (yes/no): ").strip().lower()
        return choice in ("yes", "y")

    def handle_user_message(self, user_input: str) -> str:
        """
        Process a user message and handle multi-turn tool calling.
        
        This method sends the user's message to the Gemini model and handles
        any function calls that the model wants to make. It supports chained
        tool calls where the model can make multiple tool calls in sequence
        based on the results of previous calls.
        
        Args:
            user_input (str): The user's message to process
            
        Returns:
            str: The final response text from the model after all tool calls
        """
        # Step 1: Send the user's initial message to the model
        response = self.chat_session.send_message(user_input)

        # Step 2: Handle multi-turn tool calling loop
        # Continue processing as long as the model wants to call tools
        while response.function_calls:
            tool_outputs = []
            
            # Process each function call in the response
            for tool_call in response.function_calls:
                tool_name = tool_call.name
                tool_args = tool_call.args
                
                # If sensitive → pause and request approval
                if tool_name in self.sensitive_tools:
                    self.pending_tools.append((tool_name, tool_args, response))
                    # Tell UI to wait
                    return None
                   
                # Execute the tool and capture the output
                try:
                    tool_result = self.call_tool_sync(tool_name, **tool_args)
                    # Create a successful function response part
                    tool_outputs.append(Part.from_function_response(
                        name=tool_name,
                        response={"content": tool_result}
                    ))
                except Exception as e:
                    # Create an error function response part
                    tool_outputs.append(Part.from_function_response(
                        name=tool_name,
                        response={"error": f"Error: {e}"}
                    ))

            # Send the tool outputs back to the model and get the next response
            response = self.chat_session.send_message(tool_outputs)
        
        # Step 3: Save the updated chat history after the conversation turn is complete
        self.save_chat_history()
        
        # Step 4: Return the final text response from the model
        return response.text

    def continue_after_approval(self, approved: bool) -> str:
        """
        Resume a conversation after user approval decision.
        """
        if not self.pending_tools:
            return "No pending tool requests."

        tool_name, tool_args, prev_response = self.pending_tools.pop(0)

        if not approved:
            tool_output = Part.from_function_response(
                name=tool_name,
                response={"error": "Execution denied by user"}
            )
        else:
            try:
                tool_result = self.call_tool_sync(tool_name, **tool_args)
                tool_output = Part.from_function_response(
                    name=tool_name,
                    response={"content": tool_result}
                )
            except Exception as e:
                tool_output = Part.from_function_response(
                    name=tool_name,
                    response={"error": str(e)}
                )

        response = self.chat_session.send_message([tool_output])

        # Save history and return model's text
        self.save_chat_history()
        return response.text
        
    def save_chat_history(self):
        """
        Save the current chat history to a JSON file.
        
        This method serializes the chat session history into a JSON format
        and saves it to a timestamped file. Only saves if history saving
        is enabled via the GEMINI_SAVE_CHAT_HISTORY environment variable.
        """
        # Skip saving if history saving is disabled
        if not self.save_history_enabled:
            return
        
        history_list = []
        
        # Convert GenAI Content objects to a serializable dictionary format
        for message in self.chat_session.get_history():
            # Extract text parts from each message
            text_parts = [
                {"text": part.text}
                for part in message.parts
                if hasattr(part, 'text')
            ]
            
            # Create a serializable message dictionary
            message_dict = {
                "role": message.role,
                "parts": text_parts
            }
            history_list.append(message_dict)

        # Write the chat history to a JSON file
        with open(self.chat_history, "w", encoding="utf-8") as f:
            json.dump(history_list, f, indent=4)