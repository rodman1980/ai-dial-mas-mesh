from typing import Any

from task.tools.deployment.base_agent_tool import BaseAgentTool


class WebSearchAgentTool(BaseAgentTool):
    """
    Tool for calling the Web Search Agent in the MAS mesh.
    Handles web research via DuckDuckGo search.
    """

    @property
    def deployment_name(self) -> str:
        """Deployment name matching core/config.json configuration."""
        return "web-search-agent"

    @property
    def name(self) -> str:
        """Tool name exposed to calling agents."""
        return "call_web_search_agent"

    @property
    def description(self) -> str:
        """Tool description explaining capabilities to calling agents."""
        return (
            "Call the Web Search Agent to perform web research using DuckDuckGo search. "
            "Use this when you need current information from the internet, fact-checking, "
            "or answers to questions that require up-to-date web content."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        """JSON schema for tool parameters."""
        return {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The request or question for the Web Search Agent"
                },
                "propagate_history": {
                    "type": "boolean",
                    "description": "Whether to propagate the full conversation history between agents (P2P context). If false, only the prompt is sent.",
                    "default": False
                }
            },
            "required": ["prompt"]
        }
