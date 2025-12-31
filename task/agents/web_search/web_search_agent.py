from task.agents.base_agent import BaseAgent
from task.agents.web_search._prompts import SYSTEM_PROMPT
from task.tools.base_tool import BaseTool


class WebSearchAgent(BaseAgent):
    """
    Specialized agent for web research via DuckDuckGo search.
    Can call Calculations and Content Management agents as tools for collaborative tasks.
    """

    def __init__(self, endpoint: str, tools: list[BaseTool]):
        """
        Initialize Web Search Agent.
        
        Args:
            endpoint: DIAL endpoint URL for model communication
            tools: List of tools available to this agent (DuckDuckGo MCP tools, agent tools)
        """
        super().__init__(
            endpoint=endpoint,
            system_prompt=SYSTEM_PROMPT,
            tools=tools
        )
