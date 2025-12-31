from typing import Any

from task.tools.deployment.base_agent_tool import BaseAgentTool


class ContentManagementAgentTool(BaseAgentTool):
    """
    Tool for calling the Content Management Agent in the MAS mesh.
    Handles file extraction (PDF, CSV, TXT) and RAG-based search.
    """

    @property
    def deployment_name(self) -> str:
        """Deployment name matching core/config.json configuration."""
        return "content-management-agent"

    @property
    def name(self) -> str:
        """Tool name exposed to calling agents."""
        return "call_content_management_agent"

    @property
    def description(self) -> str:
        """Tool description explaining capabilities to calling agents."""
        return (
            "Call the Content Management Agent to extract content from files (PDF, CSV, TXT) "
            "and perform RAG-based semantic search over extracted content. Use this when you need to "
            "process attached documents, search for information within files, or answer questions based on file content."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        """JSON schema for tool parameters."""
        return {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The request or question for the Content Management Agent"
                },
                "propagate_history": {
                    "type": "boolean",
                    "description": "Whether to propagate the full conversation history between agents (P2P context). If false, only the prompt is sent.",
                    "default": False
                }
            },
            "required": ["prompt"]
        }
