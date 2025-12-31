from typing import Any

from task.tools.deployment.base_agent_tool import BaseAgentTool


class CalculationsAgentTool(BaseAgentTool):
    """
    Tool for calling the Calculations Agent in the MAS mesh.
    Handles mathematical operations, Python code execution, and chart generation.
    """

    @property
    def deployment_name(self) -> str:
        """Deployment name matching core/config.json configuration."""
        return "calculations-agent"

    @property
    def name(self) -> str:
        """Tool name exposed to calling agents."""
        return "call_calculations_agent"

    @property
    def description(self) -> str:
        """Tool description explaining capabilities to calling agents."""
        return (
            "Call the Calculations Agent to perform mathematical operations, execute Python code, "
            "and generate charts. Use this for complex calculations, data analysis, visualizations, "
            "or when you need to process numerical data programmatically."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        """JSON schema for tool parameters."""
        return {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The request or question for the Calculations Agent"
                },
                "propagate_history": {
                    "type": "boolean",
                    "description": "Whether to propagate the full conversation history between agents (P2P context). If false, only the prompt is sent.",
                    "default": False
                }
            },
            "required": ["prompt"]
        }

