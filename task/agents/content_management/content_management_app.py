"""
Content Management Agent Application - Handles file extraction and RAG-based semantic search.
Exposes /chat/completions endpoint via DIAL SDK for integration with DIAL Core.
"""
import uvicorn
from aidial_sdk import DIALApp
from aidial_sdk.chat_completion import ChatCompletion, Request, Response

from task.agents.content_management.content_management_agent import ContentManagementAgent
from task.agents.content_management.tools.files.file_content_extraction_tool import FileContentExtractionTool
from task.agents.content_management.tools.rag.document_cache import DocumentCache
from task.agents.content_management.tools.rag.rag_tool import RagTool
from task.tools.base_tool import BaseTool
from task.tools.deployment.calculations_agent_tool import CalculationsAgentTool
from task.tools.deployment.web_search_agent_tool import WebSearchAgentTool
from task.utils.constants import DIAL_ENDPOINT, DEPLOYMENT_NAME


class ContentManagementApplication(ChatCompletion):
    """
    DIAL application for Content Management Agent.
    
    Initialization flow:
    1. Create tools: FileExtraction, RAG (with document cache), agent tools for peer communication
    2. Initialize ContentManagementAgent with DIAL endpoint and tools
    3. Handle /chat/completions requests by creating choice and delegating to agent
    
    Agent capabilities:
    - Extract content from PDF, CSV, TXT, HTML files
    - Perform semantic RAG search over document content
    - Handle pagination for large documents
    - Can call Calculations and Web Search agents as tools
    """
    
    async def chat_completion(self, request: Request, response: Response):
        """
        Handle chat completion request for Content Management Agent.
        
        Flow:
        1. Create response choice for streaming
        2. Initialize tools (RAG tool requires shared document cache)
        3. Create ContentManagementAgent instance
        4. Delegate request handling to agent
        5. Agent streams response through choice
        
        Args:
            request: DIAL request with messages, attachments, API key
            response: DIAL response for streaming chunks
        """
        # Create choice for streaming response to client
        with response.create_choice() as choice:
            # Initialize document cache for RAG (shared across file extraction and RAG tool)
            document_cache = DocumentCache()
            
            # Initialize tools for agent
            tools: list[BaseTool] = [
                FileContentExtractionTool(document_cache=document_cache),  # Extract file content
                RagTool(document_cache=document_cache),  # Semantic search over documents
                CalculationsAgentTool(endpoint=DIAL_ENDPOINT),  # MAS mesh: call Calculations agent
                WebSearchAgentTool(endpoint=DIAL_ENDPOINT)  # MAS mesh: call Web Search agent
            ]
            
            # Create agent instance with endpoint and tools
            agent = ContentManagementAgent(
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
    description="AI DIAL Content Management Agent",
    add_healthcheck=True,
)
app.add_chat_completion("content-management-agent", ContentManagementApplication())


# Application entry point for uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5002)
