"""
MCP (Model Context Protocol) Server Implementation

This module creates and configures a FastMCP server that exposes various tools
to AI models through the Model Context Protocol. The server provides weather
information and calculator functionality as available tools.
"""

from mcp.server.fastmcp import FastMCP
from tools.weather import get_current_weather
from tools.calculator import calculate

# Initialize the FastMCP server with a descriptive name
# This server will handle tool requests from AI models
server = FastMCP(name="mcprout")

# Register the weather tool - allows AI models to get current weather data
# for any location specified by the user
server.add_tool(get_current_weather)

# Register the calculator tool - enables AI models to perform mathematical
# calculations and return results to users
server.add_tool(calculate)

def main():
    """
    Main entry point for the MCP server.
    
    Starts the server and begins listening for tool requests from
    connected AI models. The server will run indefinitely until stopped.
    """
    server.run()

if __name__ == "__main__":
    main()