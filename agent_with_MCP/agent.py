from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
# Define the connection parameters for the remote FastMCP server
# For SSE (Server-Sent Events) connections
# mcp_server_params = SseServerParams(url="http://127.0.0.1:8001/mcp")

# The MCPToolset handles the connection to the server and exposes its tools
# Use from_server() method to create the toolset
# mcp_tool_set = MCPToolset.from_server(mcp_server_params)
mcp_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(url="http://127.0.0.1:8001/mcp/")
)
# Create the agent
root_agent = LlmAgent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    description="Agent to answer questions about the time and weather in a city.",
    instruction="You are a helpful agent who can answer user questions about the time and weather in a city.",
    tools=[mcp_toolset],
)
