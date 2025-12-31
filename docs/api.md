---
title: API Reference - AI DIAL MAS Mesh
description: Comprehensive API documentation including agent interfaces, tool schemas, and message formats
version: 1.0.0
last_updated: 2025-12-31
related: [architecture.md, README.md]
tags: [api, reference, interfaces, schemas]
---

# API Reference

## Table of Contents
- [Agent Endpoints](#agent-endpoints)
- [Message Formats](#message-formats)
- [Tool Schemas](#tool-schemas)
- [Core Classes](#core-classes)
- [Utility Functions](#utility-functions)

## Agent Endpoints

All agents expose OpenAI-compatible `/chat/completions` endpoints.

### Calculations Agent

**Endpoint:** `http://localhost:5001/openai/deployments/calculations-agent/chat/completions`

**Capabilities:**
- Simple arithmetic operations
- Python code execution
- Chart generation (Plotly)
- Data analysis

**Tools Available:**
- `simple_calculator` - Basic math operations
- `python_code_interpreter` - Execute Python code via MCP
- `call_content_management_agent` - Call Content Management Agent
- `call_web_search_agent` - Call Web Search Agent

**Example Request:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Calculate 15% of 250 and create a bar chart"
    }
  ],
  "stream": true
}
```

### Content Management Agent

**Endpoint:** `http://localhost:5002/openai/deployments/content-management-agent/chat/completions`

**Capabilities:**
- Extract content from PDF, CSV, TXT, HTML files
- Semantic search (RAG) over document content
- Handle pagination for large documents

**Tools Available:**
- `file_content_extraction` - Extract file content
- `rag_search` - Semantic search over documents
- `call_calculations_agent` - Call Calculations Agent
- `call_web_search_agent` - Call Web Search Agent

**Example Request with Attachment:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Extract key points from this document",
      "custom_content": {
        "attachments": [
          {
            "type": "application/pdf",
            "url": "files://path/to/document.pdf"
          }
        ]
      }
    }
  ],
  "stream": true
}
```

### Web Search Agent

**Endpoint:** `http://localhost:5003/openai/deployments/web-search-agent/chat/completions`

**Capabilities:**
- Web search via DuckDuckGo
- Web page content fetching
- Research synthesis with citations

**Tools Available:**
- DuckDuckGo MCP tools (dynamic from MCP server)
- `call_calculations_agent` - Call Calculations Agent
- `call_content_management_agent` - Call Content Management Agent

**Example Request:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Research the latest developments in quantum computing"
    }
  ],
  "stream": true
}
```

## Message Formats

### User Message

```typescript
{
  role: "user",
  content: string,
  custom_content?: {
    attachments?: Attachment[],
    state?: Record<string, any>
  }
}
```

### Assistant Message

```typescript
{
  role: "assistant",
  content: string,
  tool_calls?: ToolCall[],
  custom_content?: {
    state?: {
      tool_call_history: Array<any>,
      [agent_name: string]: {
        tool_call_history: Array<any>
      }
    },
    attachments?: Attachment[],
    stages?: Stage[]
  }
}
```

### Tool Message

```typescript
{
  role: "tool",
  content: string,
  tool_call_id: string,
  custom_content?: {
    state?: Record<string, any>,
    attachments?: Attachment[]
  }
}
```

### ToolCall Structure

```typescript
{
  id: string,              // Unique identifier
  type: "function",
  function: {
    name: string,          // Tool name
    arguments: string      // JSON string of parameters
  }
}
```

### Attachment Structure

```typescript
{
  type?: string,           // MIME type (e.g., "application/pdf")
  title?: string,          // Display name
  url?: string,            // Direct file URL
  reference_url?: string,  // DIAL files URL
  data?: string,           // Base64 encoded data
  index?: number           // Attachment index in response
}
```

### Stage Structure

```typescript
{
  index: number,           // Stage index
  name?: string,           // Stage display name
  content?: string,        // Stage text content
  status?: "completed",    // Stage status
  attachments?: Attachment[]
}
```

## Tool Schemas

### Simple Calculator Tool

**File:** [task/agents/calculations/tools/simple_calculator_tool.py](../task/agents/calculations/tools/simple_calculator_tool.py)

```json
{
  "type": "function",
  "function": {
    "name": "simple_calculator",
    "description": "Perform basic arithmetic operations: add, subtract, multiply, divide",
    "parameters": {
      "type": "object",
      "properties": {
        "a": {
          "type": "number",
          "description": "First operand"
        },
        "b": {
          "type": "number",
          "description": "Second operand"
        },
        "operation": {
          "type": "string",
          "enum": ["add", "subtract", "multiply", "divide"],
          "description": "Arithmetic operation to perform"
        }
      },
      "required": ["a", "b", "operation"]
    }
  }
}
```

**Example Usage:**
```python
tool_call = {
    "function": {
        "name": "simple_calculator",
        "arguments": '{"a": 15, "b": 3, "operation": "multiply"}'
    }
}
# Returns: "45"
```

### Python Code Interpreter Tool

**File:** [task/agents/calculations/tools/py_interpreter/python_code_interpreter_tool.py](../task/agents/calculations/tools/py_interpreter/python_code_interpreter_tool.py)

```json
{
  "type": "function",
  "function": {
    "name": "python_code_interpreter",
    "description": "Execute Python code with optional session management for stateful operations",
    "parameters": {
      "type": "object",
      "properties": {
        "code": {
          "type": "string",
          "description": "Python code to execute"
        },
        "session_id": {
          "type": "string",
          "description": "Optional session ID to maintain state across executions"
        }
      },
      "required": ["code"]
    }
  }
}
```

**Example Usage:**
```python
tool_call = {
    "function": {
        "name": "python_code_interpreter",
        "arguments": '''{
            "code": "import plotly.graph_objects as go\\nfig = go.Figure(data=[go.Bar(x=['A', 'B'], y=[10, 20])])\\nfig.write_html('chart.html')",
            "session_id": "session_123"
        }'''
    }
}
# Returns: Message with generated chart attachment
```

### File Content Extraction Tool

**File:** [task/agents/content_management/tools/files/file_content_extraction_tool.py](../task/agents/content_management/tools/files/file_content_extraction_tool.py)

```json
{
  "type": "function",
  "function": {
    "name": "file_content_extraction",
    "description": "Extract text content from PDF, CSV, TXT, or HTML files with pagination support",
    "parameters": {
      "type": "object",
      "properties": {
        "file_url": {
          "type": "string",
          "description": "URL or path to the file"
        },
        "page": {
          "type": "integer",
          "description": "Page number for paginated content (1-based)",
          "default": 1
        }
      },
      "required": ["file_url"]
    }
  }
}
```

**Response Format:**
```json
{
  "content": "Extracted text...",
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "has_more": true
  }
}
```

### RAG Search Tool

**File:** [task/agents/content_management/tools/rag/rag_tool.py](../task/agents/content_management/tools/rag/rag_tool.py)

```json
{
  "type": "function",
  "function": {
    "name": "rag_search",
    "description": "Perform semantic search over extracted document content using RAG",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "Search query"
        },
        "top_k": {
          "type": "integer",
          "description": "Number of top results to return",
          "default": 5
        }
      },
      "required": ["query"]
    }
  }
}
```

### Agent Tool Schema (Base)

**File:** [task/tools/deployment/base_agent_tool.py](../task/tools/deployment/base_agent_tool.py)

All agent tools (CalculationsAgentTool, ContentManagementAgentTool, WebSearchAgentTool) share this schema:

```json
{
  "type": "function",
  "function": {
    "name": "call_{agent}_agent",
    "description": "Agent-specific description",
    "parameters": {
      "type": "object",
      "properties": {
        "prompt": {
          "type": "string",
          "description": "The request or question for the agent"
        },
        "propagate_history": {
          "type": "boolean",
          "description": "Whether to propagate full P2P conversation history",
          "default": false
        }
      },
      "required": ["prompt"]
    }
  }
}
```

**Propagate History Modes:**
- `false` (one-shot): Only sends `prompt` to called agent
- `true` (P2P history): Sends full conversation history between agents

## Core Classes

### BaseAgent

**File:** [task/agents/base_agent.py](../task/agents/base_agent.py)

```python
class BaseAgent:
    """
    Base class for all agents providing core orchestration logic.
    """
    
    def __init__(
        self,
        endpoint: str,           # DIAL endpoint URL
        system_prompt: str,      # Agent's system prompt
        tools: list[BaseTool],   # Available tools
    ):
        ...
    
    async def handle_request(
        self,
        deployment_name: str,    # Model deployment name
        choice: Choice,          # Response choice for streaming
        request: Request,        # DIAL request object
        response: Response       # DIAL response object
    ) -> Message:
        """
        Main entry point for agent request handling.
        
        Flow:
        1. Prepare messages (inject system prompt, unpack history)
        2. Stream from AI model with tools
        3. Execute tool calls in parallel if present
        4. Recursively call self if tools were used
        5. Set final state and return message
        """
        ...
```

**Subclasses:**
- `CalculationsAgent` ([calculations_agent.py](../task/agents/calculations/calculations_agent.py))
- `ContentManagementAgent` ([content_management_agent.py](../task/agents/content_management/content_management_agent.py))
- `WebSearchAgent` ([web_search_agent.py](../task/agents/web_search/web_search_agent.py))

### BaseTool

**File:** [task/tools/base_tool.py](../task/tools/base_tool.py)

```python
class BaseTool(ABC):
    """
    Abstract base class for all tools.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name used in function calls."""
        ...
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for AI model."""
        ...
    
    @property
    @abstractmethod
    def parameters(self) -> dict[str, Any]:
        """JSON schema for tool parameters."""
        ...
    
    @property
    def stage_config(self) -> ToolStageConfig:
        """Optional custom stage configuration."""
        return ToolStageConfig()
    
    @property
    def schema(self) -> dict[str, Any]:
        """Complete tool schema for OpenAI format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
    
    async def execute(self, tool_call_params: ToolCallParams) -> Message:
        """
        Execute tool with error handling.
        Returns Message with tool_call_id.
        """
        ...
    
    @abstractmethod
    async def _execute(self, tool_call_params: ToolCallParams) -> str | Message:
        """
        Tool-specific implementation.
        Can return string or Message object.
        """
        ...
```

### BaseAgentTool

**File:** [task/tools/deployment/base_agent_tool.py](../task/tools/deployment/base_agent_tool.py)

```python
class BaseAgentTool(BaseTool, ABC):
    """
    Base class for agent-to-agent communication tools.
    """
    
    def __init__(self, endpoint: str):
        """Initialize with DIAL endpoint URL."""
        self.endpoint = endpoint
    
    @property
    @abstractmethod
    def deployment_name(self) -> str:
        """Agent deployment name from core config."""
        ...
    
    async def _execute(self, tool_call_params: ToolCallParams) -> Message:
        """
        Execute agent call via DIAL Unified Protocol.
        
        Flow:
        1. Parse prompt and propagate_history
        2. Prepare messages (_prepare_messages)
        3. Stream from called agent via AsyncDial
        4. Propagate stages and attachments
        5. Collect state for P2P history
        6. Return Tool message with custom_content
        """
        ...
    
    def _prepare_messages(self, tool_call_params: ToolCallParams) -> list[dict]:
        """
        Prepare message history for called agent.
        
        Modes:
        - One-shot: Single user message with prompt
        - P2P: Extract and propagate full interaction history
        """
        ...
```

## Utility Functions

### History Management

**File:** [task/utils/history.py](../task/utils/history.py)

```python
def unpack_messages(
    messages: list[Message],
    state_history: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Flatten nested tool call history from assistant messages.
    
    Process:
    1. Iterate through messages
    2. For assistant messages, extract tool_call_history from state
    3. Unpack tool and assistant messages recursively
    4. Append attachment URLs to user messages
    5. Remove custom_content before sending to model
    
    Args:
        messages: Request messages
        state_history: Accumulated tool call history
    
    Returns:
        Flattened message list ready for model consumption
    """
    ...
```

### Stage Management

**File:** [task/utils/stage.py](../task/utils/stage.py)

```python
class StageProcessor:
    """Utility for stage lifecycle management."""
    
    @staticmethod
    def open_stage(choice: Choice, name: Optional[str] = None) -> Stage:
        """
        Create and open a new stage.
        
        Args:
            choice: Response choice
            name: Optional stage name
        
        Returns:
            Opened Stage object
        """
        ...
    
    @staticmethod
    def close_stage_safely(stage: Stage) -> None:
        """
        Safely close a stage with error handling.
        Prevents exceptions if stage already closed.
        """
        ...
```

### Constants

**File:** [task/utils/constants.py](../task/utils/constants.py)

```python
# DIAL Configuration
DIAL_ENDPOINT = os.getenv('DIAL_ENDPOINT', "http://localhost:8080")
DEPLOYMENT_NAME = os.getenv('DEPLOYMENT_NAME', 'gpt-4o')

# State Keys
TOOL_CALL_HISTORY_KEY = "tool_call_history"  # Key for tool history in state
CUSTOM_CONTENT = "custom_content"             # Key for custom content field
```

## Data Models

### ToolCallParams

**File:** [task/tools/models.py](../task/tools/models.py)

```python
@dataclass
class ToolCallParams:
    """Parameters passed to tool execution."""
    tool_call: ToolCall              # Tool call from model
    stage: Stage                     # Stage for streaming content
    choice: Choice                   # Choice for attachments/stages
    api_key: str                     # DIAL API key
    conversation_id: str             # Conversation ID header
    messages: list[Message]          # Request messages
```

### ToolStageConfig

```python
@dataclass
class ToolStageConfig:
    """Configuration for tool stage display."""
    create_stage: bool = True               # Whether to create stage
    show_request_in_stage: bool = True      # Show tool arguments
    show_response_in_stage: bool = True     # Show tool response
    stage_name: Optional[str] = None        # Custom stage name
```

## Error Handling

All tools and agents implement error handling:

```python
try:
    result = await tool._execute(tool_call_params)
except Exception as e:
    # Log error
    print(f"Error in tool {tool.name}: {e}")
    # Return error message
    return Message(
        role=Role.TOOL,
        content=f"Error: {str(e)}",
        tool_call_id=tool_call.id
    )
```

## Response Streaming

Agents stream responses in chunks:

```python
async for chunk in stream:
    if chunk.choices and len(chunk.choices) > 0:
        delta = chunk.choices[0].delta
        
        # Stream content
        if delta.content:
            choice.append_content(delta.content)
        
        # Handle tool calls
        if delta.tool_calls:
            # Accumulate tool call deltas
            ...
        
        # Handle custom content
        if delta.custom_content:
            # Process state, attachments, stages
            ...
```

## Feature-to-Code-to-Test Traceability

| Feature | Implementation | Test File |
|---------|---------------|-----------|
| Agent-to-Agent Communication | [base_agent_tool.py](../task/tools/deployment/base_agent_tool.py) | TODO: requires confirmation |
| Python Code Execution | [python_code_interpreter_tool.py](../task/agents/calculations/tools/py_interpreter/python_code_interpreter_tool.py) | TODO: requires confirmation |
| File Content Extraction | [file_content_extraction_tool.py](../task/agents/content_management/tools/files/file_content_extraction_tool.py) | TODO: requires confirmation |
| RAG Search | [rag_tool.py](../task/agents/content_management/tools/rag/rag_tool.py) | TODO: requires confirmation |
| Weather Chart Use Case | [calculations_agent.py](../task/agents/calculations/calculations_agent.py) + [web_search_agent.py](../task/agents/web_search/web_search_agent.py) | Manual test scenario |
| PDF Question Answering | [content_management_agent.py](../task/agents/content_management/content_management_agent.py) | Manual test with [tests/java-questions-150.pdf](../tests/java-questions-150.pdf) |

---

*Last updated: 2025-12-31 | Version: 1.0.0*
