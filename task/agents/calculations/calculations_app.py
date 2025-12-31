"""
Calculations Agent Application - Handles math operations, Python code execution, and chart generation.
Exposes /chat/completions endpoint via DIAL SDK for integration with DIAL Core.
"""
import os

import uvicorn
from aidial_sdk import DIALApp
from aidial_sdk.chat_completion import ChatCompletion, Request, Response

from task.agents.calculations.calculations_agent import CalculationsAgent
from task.agents.calculations.tools.simple_calculator_tool import SimpleCalculatorTool
from task.tools.base_tool import BaseTool
from task.agents.calculations.tools.py_interpreter.python_code_interpreter_tool import PythonCodeInterpreterTool
from task.tools.deployment.content_management_agent_tool import ContentManagementAgentTool
from task.tools.deployment.web_search_agent_tool import WebSearchAgentTool
from task.utils.constants import DIAL_ENDPOINT, DEPLOYMENT_NAME

# MCP server URL for Python code interpreter
_PYTHON_INTERPRETER_MCP_URL = os.getenv('PYTHON_INTERPRETER_MCP_URL', "http://localhost:8050/mcp")


class CalculationsApplication(ChatCompletion):
    """
    DIAL application for Calculations Agent.
    
    Initialization flow:
    1. Create tools: SimpleCalculator, PythonInterpreter (async factory), agent tools for peer communication
    2. Initialize CalculationsAgent with DIAL endpoint and tools
    3. Handle /chat/completions requests by creating choice and delegating to agent
    
    Agent capabilities:
    - Simple arithmetic operations
    - Python code execution for complex calculations
    - Chart generation and data visualization
    - Can call Content Management and Web Search agents as tools
    """
    
    async def chat_completion(self, request: Request, response: Response):
        """
        Handle chat completion request for Calculations Agent.
        
        Flow:
        1. Create response choice for streaming
        2. Initialize tools (Python interpreter requires async factory)
        3. Create CalculationsAgent instance
        4. Delegate request handling to agent
        5. Agent streams response through choice
        
        Args:
            request: DIAL request with messages, attachments, API key
            response: DIAL response for streaming chunks
        """
        # Create choice for streaming response to client
        with response.create_choice() as choice:
            # Initialize tools for agent
            tools: list[BaseTool] = [
                SimpleCalculatorTool(),
                await PythonCodeInterpreterTool.create(_PYTHON_INTERPRETER_MCP_URL),  # Async factory pattern
                ContentManagementAgentTool(endpoint=DIAL_ENDPOINT),  # MAS mesh: call Content Management agent
                WebSearchAgentTool(endpoint=DIAL_ENDPOINT)  # MAS mesh: call Web Search agent
            ]
            
            # Create agent instance with endpoint and tools
            agent = CalculationsAgent(
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
    description="AI DIAL Calculations Agent",
    add_healthcheck=True,
)
app.add_chat_completion("calculations-agent", CalculationsApplication())


# Application entry point for uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5001)