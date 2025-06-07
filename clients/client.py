# import asyncio
from typing import Optional
import logging
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from utils.helpers import HelperFunctions
from clients.llm_interface import LLMInterface

from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()  # Load environment variables from .env file

class MCPClient:
    def __init__(self):
        """Initialize session and LLM Client."""
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connect_to_server(self, server_script_path: str):
        """Conncet to MCP server
        
        Args:
            server_script_path: Path to the server script.
        """

        if not (server_script_path.endswith(".py")):
            raise ValueError("Server script must be a python script")
        
        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path],
            env=None
        )

        # Initialize communication between client and MCP server
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        # Initialize a client session to communicate with the MCP server
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List all available tools
        tools_result = await self.session.list_tools()
        tools = tools_result.tools
        logging.info(f"Connected to server with tools: {', '.join(tool.name for tool in tools)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()



async def start_chat(server_script_path: str):
    """Start an interactive chat session using MCP client and LLM interface."""
    mcp_client = MCPClient()
    try:
        await mcp_client.connect_to_server(server_script_path)

        tools_response = await mcp_client.session.list_tools()
        tools = tools_response.tools
        tools_formatted = "\n".join(
            f"{HelperFunctions.format_tool(t.name, t.description, t.inputSchema)}"
            for t in tools
        )

        llm_interface = LLMInterface()

        while True:
            user_query = input("\nEnter your query (type 'exit' to leave the chat):\n")
            if user_query.lower() in ("exit", "quit"):
                break
            
            llm_interface.history.append({"role": "user", "content": user_query})
            llm_response = await llm_interface.get_llm_response(
                tools_description=tools_formatted
            )
            parsed_response = await llm_interface.process_llm_response(
                llm_response=llm_response
            )

            if parsed_response.get("tool_call"):
                tool_calls = parsed_response.get("tool_call_data", [])
                # Execute tool calls
                tool_results = []
                for tool_call in tool_calls:
                    tool_name = tool_call.get("tool")
                    tool_args = tool_call.get("arguments")
                    result = await mcp_client.session.call_tool(tool_name, tool_args)
                    tool_results.append(result.content[0].text)

                llm_interface.history.append(
                    {"role": "system", "content": f"{tool_results=}"}
                )

                # Re-query the LLM with tool results
                llm_response = await llm_interface.get_llm_response(
                    tools_description=tools_formatted
                )
                parsed_response = await llm_interface.process_llm_response(
                    llm_response=llm_response
                )

            user_message = parsed_response.get("message_to_user")
            if user_message:
                print(f"\n\nAssistant:\n{user_message}\n")
    finally:
        await mcp_client.cleanup()