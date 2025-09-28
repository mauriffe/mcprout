# MCPRout - Gemini Chatbot with MCP Tools

A Streamlit-based chatbot application that integrates Google's Gemini AI with Model Context Protocol (MCP) tools for enhanced functionality. The application provides a web interface for interacting with Gemini models while having access to custom tools like weather information and mathematical calculations.

## Features

- 🤖 **Gemini AI Integration**: Support for multiple Gemini models (2.5 Pro, 2.5 Flash, 2.5 Flash Lite)
- 🛠️ **MCP Tools**: Extensible tool system using Model Context Protocol
- 💬 **Modern Chat Interface**: Beautiful, responsive chat UI with custom styling
- 🔧 **Configurable System Instructions**: Customizable AI behavior and responses
- 📱 **Docker Support**: Easy deployment with Docker and Docker Compose
- 💾 **Chat History**: Optional conversation history saving
- ⚡ **Real-time Responses**: Live typing indicators and smooth message flow

## Available Tools

- **Calculator**: Perform mathematical calculations and expressions
- **Weather**: Get current weather information for any location (demo implementation)

## Prerequisites

- Python 3.13+
- Google Gemini API key
- Docker (optional, for containerized deployment)

## Installation

### Local Development

1. **Clone or navigate to the project directory**:
   ```bash
   cd mcprout
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the project root (recommended):
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_SAVE_CHAT_HISTORY=false
   ```
   
   Alternatively, you can set environment variables directly in your system. The application will first check for a `.env` file, then fall back to system environment variables.

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

5. **Access the application**:
   Open your browser and navigate to `http://localhost:8501`

### Docker Deployment

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

2. **Access the application**:
   Open your browser and navigate to `http://localhost:8501`

## Configuration

### Model Selection
Choose from available Gemini models in the sidebar:
- `gemini-2.5-pro`: Most capable model for complex tasks
- `gemini-2.5-flash`: Balanced performance and speed
- `gemini-2.5-flash-lite`: Fastest model for simple queries

### System Instructions
Customize the AI's behavior by modifying the system instructions in the sidebar. The default instructions focus on weather and calculation assistance.

### Environment Variables
- `GEMINI_API_KEY`: Your Google Gemini API key (required)
- `GEMINI_SAVE_CHAT_HISTORY`: Set to "true" to save chat history to JSON files

## Project Structure

```
mcprout/
├── app.py                 # Main Streamlit application
├── mcp_server.py         # MCP server for tool integration
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose setup
├── core/
│   ├── chat_handler.py  # Chat logic and Gemini integration
│   └── config.py        # Configuration utilities
├── tools/
│   ├── calculator.py    # Mathematical calculation tool
│   └── weather.py       # Weather information tool
├── data/
│   └── system_instruction.txt  # Default system instructions
└── utils/               # Utility functions
```

## Adding New Tools

To add a new tool to the MCP server:

1. **Create a new tool file** in the `tools/` directory
2. **Define your function** with proper type hints and docstring
3. **Create a FunctionDeclaration** for the tool
4. **Add the tool to the MCP server** in `mcp_server.py`
5. **Import and register** the tool in the server

Example tool structure:
```python
from google.genai.types import FunctionDeclaration

def my_tool(param: str) -> str:
    """Tool description."""
    # Tool implementation
    return "result"

my_tool_declaration = FunctionDeclaration(
    name="my_tool",
    description="Tool description",
    parameters={
        "type": "OBJECT",
        "properties": {
            "param": {"type": "string", "description": "Parameter description"},
        },
        "required": ["param"],
    },
)
```

## Development

### Running in Development Mode
```bash
streamlit run app.py --server.runOnSave true
```

### Chat History
When `GEMINI_SAVE_CHAT_HISTORY` is enabled, chat sessions are saved to `data/chat_history{timestamp}.json` files.

### Customization
- Modify `app.py` for UI changes
- Update `core/chat_handler.py` for chat logic
- Add tools in the `tools/` directory
- Customize styling in the CSS section of `app.py`

## Troubleshooting

### Common Issues

1. **API Key Error**: Ensure `GEMINI_API_KEY` is set in your environment
2. **Port Already in Use**: Change the port in `docker-compose.yml` or use `--server.port` with Streamlit
3. **Tool Not Found**: Verify tools are properly registered in `mcp_server.py`

### Logs
Check the Streamlit logs in the terminal or Docker logs for debugging information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Please check the license file for details.

## Support

For help and support:
- Check the [Help Documentation](https://martinmoreau.tech/help)
- Report bugs at [Bug Tracker](https://martinmoreau.tech/bug)

---

**Note**: This is an experimental project that demonstrates the integration of Gemini AI with MCP tools. The weather tool is a demo implementation and returns static data.
