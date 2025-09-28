#####for gemini
from google.genai import Client as GeminiClient
from google.genai.types import GenerateContentConfig, Tool, Part,FunctionDeclaration
import json
import os
from datetime import datetime
from dotenv import load_dotenv

#####for mcp
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters
import asyncio

class ChatHandler:
    def __init__(self, system_instructions: str = "", model_choice: str = "gemini-2.5-flash-lite"):
        """Initializes the chat handler with tools and an initial chat history."""
        # Load environment variables from .env file if present
        load_dotenv()
        self.gemini_model = model_choice
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set in .env file or environment variables.")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        self.save_history_enabled = os.getenv("GEMINI_SAVE_CHAT_HISTORY", "false").lower() in ("true", "1", "yes")
        self.chat_history = f"data/chat_history{timestamp}.json"
        self.system_instruction = system_instructions  # Or set a default value
        self.available_tools, function_declarations = self._get_mcp_tools()
        self.chat_tools = Tool(function_declarations=function_declarations)
        self.client = GeminiClient(api_key=self.api_key)

        # Create the chat session with the defined tools
        self.chat_session = self.client.chats.create(
            model=self.gemini_model,
            config=GenerateContentConfig(temperature=0,system_instruction=self.system_instruction,tools=[self.chat_tools]),
            history=[]
        )

    def _get_mcp_tools(self):
        """Synchronously retrieve tool definitions from MCP."""
        async def _fetch_tools():
            server_params = StdioServerParameters(
                command="python",
                args=["mcp_server.py"],
            )
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    mcp_tools = await session.list_tools()
                    # List available tools
                    available_tools = [tool.name for tool in mcp_tools.tools]
                    # Generate tool declaration for all available tools
                    all_tools_dec = []
                    for tool in mcp_tools.tools:
                        params = {
                            k: v
                            for k, v in tool.inputSchema.items()
                            if k not in ["additionalProperties", "$schema"]
                        }
                        all_tools_dec.append(
                            FunctionDeclaration(
                                    name=tool.name,
                                    description=tool.description,
                                    parameters= params
                                )
                            )
                    return available_tools, all_tools_dec  # <-- return list of tools and full tool definitions

        return asyncio.run(_fetch_tools())

    async def call_tool_async(self, tool_name: str, **kwargs):
        """
        Async call to a tool via MCP stdio client.
        """
        server_params = StdioServerParameters(command="python",
                args=["mcp_server.py"],)
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()
               
                if tool_name not in self.available_tools:
                    raise ValueError(f"Tool '{tool_name}' not found. Available tools: {self.available_tools}")
                
                # Call the tool
                result = await session.call_tool(tool_name, arguments=kwargs)
                return result

    def call_tool_sync(self, tool_name: str, **kwargs):
        """
        Synchronous wrapper for calling an MCP tool.
        """
        return asyncio.run(self.call_tool_async(tool_name, **kwargs))


    def handle_user_message(self, user_input: str) -> str:
        """Sends a message to the model and handles chained tool calls."""

        # 1. Send the user's initial message
        response = self.chat_session.send_message(
            user_input
        )

        # 2. Loop to handle multi-turn tool use
        while response.function_calls:
            tool_outputs = []
            for tool_call in response.function_calls:
                tool_name = tool_call.name
                tool_args = tool_call.args
                # Execute the tool and capture the output
                try:
                    tool_result = self.call_tool_sync(tool_name, **tool_args)
                    tool_outputs.append(Part.from_function_response(
                        name= tool_name,
                        response={ "content": tool_result}
                    ))
                except Exception as e:
                    tool_outputs.append(Part.from_function_response(
                        name= tool_name,
                        response={"error": f"Error: {e}"}
                    ))

            # Send the tool outputs back to the model and get the next response
            response = self.chat_session.send_message(tool_outputs)
        # 3. Save the updated chat history after the conversation turn is complete
        self.save_chat_history()
        # 3. Return the final text response from the model
        return response.text

    def save_chat_history(self):
        """Saves the chat history to a JSON file."""
        if not self.save_history_enabled:
            return
        history_list = []
        # Convert GenAI Content objects to a serializable dictionary format
        for message in self.chat_session.get_history():
            message_dict = {
                "role": message.role,
                "parts": [
                    {"text": part.text}
                    for part in message.parts
                    if hasattr(part, 'text')
                ]
            }
            history_list.append(message_dict)

        with open(self.chat_history, "w", encoding="utf-8") as f:
            json.dump(history_list, f, indent=4)