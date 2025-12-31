"""
Web Search Agent Application - Handles web research via DuckDuckGo search.
Exposes /chat/completions endpoint via DIAL SDK for integration with DIAL Core.
"""
import os

import uvicorn
from aidial_sdk import DIALApp
from aidial_sdk.chat_completion import ChatCompletion, Request, Response

from task.agents.web_search.web_search_agent import WebSearchAgent
from task.tools.base_tool import BaseTool
from task.tools.deployment.calculations_agent_tool import CalculationsAgentTool
from task.tools.deployment.content_management_agent_tool import ContentManagementAgentTool
from task.tools.mcp.mcp_client import MCPClient
from task.tools.mcp.mcp_tool import MCPTool
from task.utils.constants import DIAL_ENDPOINT, DEPLOYMENT_NAME

# MCP server URL for DuckDuckGo web search
_DDG_MCP_URL = os.getenv('DDG_MCP_URL', "http://localhost:8051/mcp")


class WebSearchApplication(ChatCompletion):
    """
    DIAL application for Web Search Agent.
    
    Initialization flow:
    1. Connect to DuckDuckGo MCP server and retrieve available tools
    2. Wrap MCP tools in MCPTool instances for agent use
    3. Add agent tools for peer communication (Calculations, Content Management)
    4. Initialize WebSearchAgent with DIAL endpoint and tools
    5. Handle /chat/completions requests by creating choice and delegating to agent
    
    Agent capabilities:
    - Web search via DuckDuckGo MCP server
    - Research synthesis with source citations
    - Can call Calculations and Content Management agents as tools
    """
    
    async def chat_completion(self, request: Request, response: Response):
        """
        Handle chat completion request for Web Search Agent.
        
        Flow:
        1. Create response choice for streaming
        2. Connect to DuckDuckGo MCP server
        3. Retrieve and wrap MCP tools
        4. Add agent tools for MAS mesh communication
        5. Create WebSearchAgent instance
        6. Delegate request handling to agent
        7. Agent streams response through choice
        
        Args:
            request: DIAL request with messages, API key
            response: DIAL response for streaming chunks
        """
        # Create choice for streaming response to client
        with response.create_choice() as choice:
            # Connect to DuckDuckGo MCP server and get available tools
            async with MCPClient(_DDG_MCP_URL) as mcp_client:
                mcp_tools_models = await mcp_client.get_tools()
                
                # Wrap MCP tools for agent use
                mcp_tools: list[BaseTool] = [
                    MCPTool(
                        tool_model=tool_model,
                        mcp_client=mcp_client
                    )
                    for tool_model in mcp_tools_models
                ]
                
                # Add agent tools for MAS mesh communication
                tools: list[BaseTool] = [
                    *mcp_tools,  # DuckDuckGo search tools
                    CalculationsAgentTool(endpoint=DIAL_ENDPOINT),  # MAS mesh: call Calculations agent
                    ContentManagementAgentTool(endpoint=DIAL_ENDPOINT)  # MAS mesh: call Content Management agent
                ]
                
                # Create agent instance with endpoint and tools
                agent = WebSearchAgent(
                    endpoint=DIAL_ENDPOINT,
                    tools=tools
                )
                
                # Handle request through agent (streams response to choice)
                await agent.handle_request(
                    deployment_name=DEPLOYMENT_NAME,
                    choice=choice,
                    request=request,
                    response=response
                )


# Create DIAL application with deployment name matching core/config.json
app = DIALApp(
    description="AI DIAL Web Search Agent",
    add_healthcheck=True,
)
app.add_chat_completion("web-search-agent", WebSearchApplication())


# Application entry point for uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5003)
