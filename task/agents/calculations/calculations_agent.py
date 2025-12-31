from task.agents.base_agent import BaseAgent
from task.agents.calculations._prompts import SYSTEM_PROMPT
from task.tools.base_tool import BaseTool


class CalculationsAgent(BaseAgent):
    """
    Specialized agent for mathematical operations, Python code execution, and chart generation.
    Can call Web Search and Content Management agents as tools for collaborative tasks.
    """

    def __init__(self, endpoint: str, tools: list[BaseTool]):
        """
        Initialize Calculations Agent.
        
        Args:
            endpoint: DIAL endpoint URL for model communication
            tools: List of tools available to this agent (calculator, Python interpreter, agent tools)
        """
        super().__init__(
            endpoint=endpoint,
            system_prompt=SYSTEM_PROMPT,
            tools=tools
        )