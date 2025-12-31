from task.agents.base_agent import BaseAgent
from task.agents.content_management._prompts import SYSTEM_PROMPT
from task.tools.base_tool import BaseTool


class ContentManagementAgent(BaseAgent):
    """
    Specialized agent for file extraction (PDF, CSV, TXT) and RAG-based semantic search.
    Can call Calculations and Web Search agents as tools for collaborative tasks.
    """

    def __init__(self, endpoint: str, tools: list[BaseTool]):
        """
        Initialize Content Management Agent.
        
        Args:
            endpoint: DIAL endpoint URL for model communication
            tools: List of tools available to this agent (file extraction, RAG, agent tools)
        """
        super().__init__(
            endpoint=endpoint,
            system_prompt=SYSTEM_PROMPT,
            tools=tools
        )
