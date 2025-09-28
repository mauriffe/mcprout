from mcp.server.fastmcp import FastMCP
from tools.weather import get_current_weather
from tools.calculator import calculate

# Create an instance of the FastMCP server
servertest = FastMCP(name="MyToolServer")

# Add your getweather function as a tool
servertest.add_tool(get_current_weather)

# Add your calculate function as a tool
servertest.add_tool(calculate)

# Run the server
def main():
    servertest.run()

if __name__ == "__main__":
    main()