---
title: Setup Guide - AI DIAL MAS Mesh
description: Comprehensive environment setup, configuration, and deployment instructions
version: 1.0.0
last_updated: 2025-12-31
related: [README.md, architecture.md, testing.md]
tags: [setup, installation, configuration, deployment]
---

# Setup Guide

## Table of Contents
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Configuration](#configuration)
- [Running the System](#running-the-system)
- [Development Workflow](#development-workflow)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Agent applications |
| Docker | 24.0+ | Container orchestration |
| Docker Compose | 2.20+ | Multi-service deployment |
| Git | 2.30+ | Version control |

### System Requirements

- **OS**: macOS, Linux, or Windows with WSL2
- **Memory**: Minimum 8GB RAM (16GB recommended)
- **Disk**: 10GB free space
- **Network**: Internet access for downloading images and API calls

### Required Credentials

- **DIAL API Key**: Obtain from AI DIAL platform for GPT-4o model access

## Environment Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd ai-dial-mas-mesh
```

### 2. Create Virtual Environment

```bash
# Create virtual environment with Python 3.12
python3.12 -m venv dial_mas_mesh

# Activate virtual environment
# macOS/Linux:
source dial_mas_mesh/bin/activate

# Windows:
dial_mas_mesh\Scripts\activate
```

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt
```

**Dependencies installed:**
```
aidial-sdk==0.27.0          # DIAL SDK for agents
aidial-client==0.3.0        # DIAL client for agent-to-agent calls
mcp==1.20.0                 # Model Context Protocol
pydantic==2.12.3            # Data validation
faiss-cpu==1.12.0           # Vector similarity search
sentence-transformers==5.1.2 # Text embeddings
beautifulsoup4==4.14.2      # HTML parsing
pdfplumber==0.11.7          # PDF extraction
numpy==2.3.4                # Numerical operations
pandas==2.3.3               # Data manipulation
tabulate==0.9.0             # Table formatting
langchain==1.0.3            # LLM framework
langchain-text-splitters==1.0.0 # Text chunking
```

### 4. Verify Installation

```bash
# Check Python version
python --version
# Expected output: Python 3.12.x

# Verify dependencies
pip list | grep aidial
# Expected output:
# aidial-client    0.3.0
# aidial-sdk       0.27.0

# Test imports
python -c "from aidial_sdk import DIALApp; from aidial_client import AsyncDial; print('✓ Imports successful')"
```

## Configuration

### 1. DIAL Core Configuration

Edit `core/config.json` to configure models and agents:

#### Add GPT-4o Model

```json
{
  "models": {
    "gpt-4o": {
      "displayName": "GPT 4o",
      "endpoint": "http://adapter-dial:5000/openai/deployments/gpt-4o/chat/completions",
      "iconUrl": "http://localhost:3001/gpt4.svg",
      "type": "chat",
      "upstreams": [
        {
          "endpoint": "https://ai-proxy.lab.epam.com/openai/deployments/gpt-4o/chat/completions",
          "key": "YOUR_DIAL_API_KEY_HERE"
        }
      ]
    }
  }
}
```

**⚠️ Important**: Replace `YOUR_DIAL_API_KEY_HERE` with your actual DIAL API key.

#### Add Agent Applications

```json
{
  "applications": {
    "calculations-agent": {
      "displayName": "Calculations Agent",
      "description": "Calculations Agent. Primary goal to work with calculations. Capable to make plotly graphics and chart bars. Equipped with: Python Code Interpreter (via MCP), and Simple calculator.",
      "endpoint": "http://host.docker.internal:5001/openai/deployments/calculations-agent/chat/completions",
      "inputAttachmentTypes": [
        "application/pdf",
        "text/html",
        "text/plain",
        "text/csv"
      ],
      "forwardAuthToken": true
    },
    "content-management-agent": {
      "displayName": "Content Management Agent",
      "description": "Content Management Agent. Equipped with: Files content extractor and RAG search (supports PDF, TXT, CSV files).",
      "endpoint": "http://host.docker.internal:5002/openai/deployments/content-management-agent/chat/completions",
      "inputAttachmentTypes": [
        "application/pdf",
        "text/html",
        "text/plain",
        "text/csv"
      ],
      "forwardAuthToken": true
    },
    "web-search-agent": {
      "displayName": "WEB Search Agent",
      "description": "WEB Search Agent. Performs research in WEB based on the user request. Equipped with: WEB search (DuckDuckGo via MCP) and is able to fetch WEB pages content.",
      "endpoint": "http://host.docker.internal:5003/openai/deployments/web-search-agent/chat/completions",
      "inputAttachmentTypes": [
        "application/pdf",
        "text/html",
        "text/plain",
        "text/csv"
      ],
      "forwardAuthToken": true
    }
  }
}
```

#### Complete Configuration Template

```json
{
  "routes": {},
  "applications": {
    "calculations-agent": { /* as above */ },
    "content-management-agent": { /* as above */ },
    "web-search-agent": { /* as above */ }
  },
  "models": {
    "gpt-4o": { /* as above */ }
  },
  "keys": {
    "dial_api_key": {
      "project": "TEST-PROJECT",
      "role": "default"
    }
  },
  "roles": {
    "default": {
      "limits": {}
    }
  }
}
```

### 2. Environment Variables

Optional environment variables for customization:

```bash
# MCP Server URLs (defaults shown)
export PYTHON_INTERPRETER_MCP_URL="http://localhost:8050/mcp"
export DDG_MCP_URL="http://localhost:8051/mcp"

# DIAL Configuration
export DIAL_ENDPOINT="http://localhost:8080"
export DEPLOYMENT_NAME="gpt-4o"

# Logging
export LOG_LEVEL="INFO"
```

### 3. Docker Compose Configuration

The `docker-compose.yml` is pre-configured. Key services:

```yaml
services:
  core:                    # DIAL Core (port 8080)
  chat:                    # Chat UI (port 3000)
  themes:                  # UI themes (port 3001)
  redis:                   # Cache (port 6379)
  redis-insight:           # Redis UI (port 6380)
  adapter-dial:            # DIAL adapter (internal)
  python-interpreter-mcp-server:  # MCP (port 8050)
  ddg-search-mcp-server:   # MCP (port 8051)
```

## Running the System

### Start All Services

```bash
# Start all Docker services
docker-compose up

# Start in detached mode (background)
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f core
```

**Expected output:**
```
✓ core                     Started
✓ chat                     Started
✓ themes                   Started
✓ redis                    Started
✓ python-interpreter-mcp-server Started
✓ ddg-search-mcp-server    Started
```

### Start Agent Applications

In separate terminals (with virtual environment activated):

#### Terminal 1: Calculations Agent
```bash
source dial_mas_mesh/bin/activate
python -m task.agents.calculations.calculations_app
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:5001
```

#### Terminal 2: Content Management Agent
```bash
source dial_mas_mesh/bin/activate
python -m task.agents.content_management.content_management_app
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:5002
```

#### Terminal 3: Web Search Agent
```bash
source dial_mas_mesh/bin/activate
python -m task.agents.web_search.web_search_app
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:5003
```

### Verify System Health

```bash
# Check Docker services
docker-compose ps

# Expected output (all services "Up")
NAME                            STATUS
ai-dial-mas-mesh-chat-1         Up
ai-dial-mas-mesh-core-1         Up
ai-dial-mas-mesh-redis-1        Up
...

# Check agent endpoints
curl http://localhost:5001/health
curl http://localhost:5002/health
curl http://localhost:5003/health

# Access Chat UI
open http://localhost:3000
```

### Stop Services

```bash
# Stop Docker services
docker-compose down

# Stop with volume cleanup
docker-compose down -v

# Stop agent applications
# Press Ctrl+C in each terminal
```

## Development Workflow

### Running Agents in Development Mode

```bash
# Enable auto-reload for development
uvicorn task.agents.calculations.calculations_app:app --reload --port 5001

# With custom log level
uvicorn task.agents.calculations.calculations_app:app --reload --port 5001 --log-level debug
```

### Code Structure for Development

```
task/
├── agents/                      # Agent implementations
│   ├── base_agent.py           # Extend this for new agents
│   └── {agent_name}/
│       ├── _prompts.py         # System prompt
│       ├── {agent_name}_agent.py    # Agent class
│       ├── {agent_name}_app.py      # FastAPI app
│       └── tools/              # Agent-specific tools
│
├── tools/                       # Tool implementations
│   ├── base_tool.py            # Extend this for new tools
│   ├── deployment/             # Agent tools (P2P)
│   └── mcp/                    # MCP tool wrapper
│
└── utils/                       # Shared utilities
    ├── history.py              # Message history management
    ├── stage.py                # Stage lifecycle
    └── constants.py            # Configuration constants
```

### Creating a New Agent

1. **Create agent directory**:
   ```bash
   mkdir -p task/agents/my_agent/tools
   ```

2. **Define system prompt** (`_prompts.py`):
   ```python
   SYSTEM_PROMPT = """You are a specialized agent for..."""
   ```

3. **Implement agent class** (`my_agent.py`):
   ```python
   from task.agents.base_agent import BaseAgent
   from task.agents.my_agent._prompts import SYSTEM_PROMPT

   class MyAgent(BaseAgent):
       def __init__(self, endpoint: str, tools: list[BaseTool]):
           super().__init__(
               endpoint=endpoint,
               system_prompt=SYSTEM_PROMPT,
               tools=tools
           )
   ```

4. **Create application** (`my_agent_app.py`):
   ```python
   from aidial_sdk import DIALApp
   from aidial_sdk.chat_completion import ChatCompletion, Request, Response

   class MyAgentApplication(ChatCompletion):
       async def chat_completion(self, request: Request, response: Response):
           with response.create_choice() as choice:
               tools = [...]  # Initialize tools
               agent = MyAgent(endpoint=DIAL_ENDPOINT, tools=tools)
               await agent.handle_request(
                   deployment_name=DEPLOYMENT_NAME,
                   choice=choice,
                   request=request,
                   response=response
               )

   app = DIALApp(description="My Agent")
   app.add_chat_completion("my-agent", MyAgentApplication())

   if __name__ == "__main__":
       import uvicorn
       uvicorn.run(app, host="0.0.0.0", port=5004)
   ```

5. **Add to core config**:
   ```json
   {
     "applications": {
       "my-agent": {
         "displayName": "My Agent",
         "endpoint": "http://host.docker.internal:5004/openai/deployments/my-agent/chat/completions",
         "forwardAuthToken": true
       }
     }
   }
   ```

### Creating a New Tool

1. **Extend BaseTool**:
   ```python
   from task.tools.base_tool import BaseTool
   from task.tools.models import ToolCallParams

   class MyTool(BaseTool):
       @property
       def name(self) -> str:
           return "my_tool"

       @property
       def description(self) -> str:
           return "Description of what the tool does"

       @property
       def parameters(self) -> dict:
           return {
               "type": "object",
               "properties": {
                   "param1": {"type": "string", "description": "..."}
               },
               "required": ["param1"]
           }

       async def _execute(self, tool_call_params: ToolCallParams) -> str:
           args = json.loads(tool_call_params.tool_call.function.arguments)
           # Implement tool logic
           return "result"
   ```

## Troubleshooting

### Common Issues

#### Issue: Port Already in Use

**Symptom:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:8080: bind: address already in use
```

**Solution:**
```bash
# Find process using port
lsof -i :8080
# or
netstat -tulpn | grep 8080

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

#### Issue: Agent Not Connecting to DIAL Core

**Symptom:**
```
Connection refused to http://host.docker.internal:5001
```

**Solution:**
1. Verify agent is running:
   ```bash
   curl http://localhost:5001/health
   ```

2. Check `host.docker.internal` resolution:
   ```bash
   # Inside Docker container
   docker exec -it ai-dial-mas-mesh-core-1 ping host.docker.internal
   ```

3. Alternative: Use host IP instead of `host.docker.internal`:
   ```bash
   # Get host IP
   ipconfig getifaddr en0  # macOS
   hostname -I            # Linux
   ```

#### Issue: DIAL API Key Invalid

**Symptom:**
```
401 Unauthorized: Invalid API key
```

**Solution:**
1. Verify key in `core/config.json`
2. Check key format (no extra spaces/quotes)
3. Test key with curl:
   ```bash
   curl -H "Authorization: Bearer YOUR_KEY" \
        https://ai-proxy.lab.epam.com/openai/deployments/gpt-4o/chat/completions
   ```

#### Issue: Python Interpreter MCP Timeout

**Symptom:**
```
MCP connection timeout to http://localhost:8050/mcp
```

**Solution:**
```bash
# Check MCP server logs
docker-compose logs python-interpreter-mcp-server

# Restart MCP server
docker-compose restart python-interpreter-mcp-server

# Increase timeout (if needed)
# Edit tool configuration in agent app
```

#### Issue: Import Errors

**Symptom:**
```
ModuleNotFoundError: No module named 'aidial_sdk'
```

**Solution:**
```bash
# Verify virtual environment is activated
which python
# Should show path to dial_mas_mesh/bin/python

# Reinstall dependencies
pip install -r requirements.txt

# Run from project root
cd /path/to/ai-dial-mas-mesh
python -m task.agents.calculations.calculations_app
```

### Debug Mode

Enable detailed logging:

```bash
# Set environment variable
export LOG_LEVEL=DEBUG

# Run agent with debug output
python -m task.agents.calculations.calculations_app

# View request/response details
# Check console output for:
# - Request messages
# - Tool calls
# - Response chunks
```

### Health Checks

```bash
# Check all services
./scripts/health_check.sh  # TODO: Create script

# Manual checks
curl http://localhost:8080/health          # DIAL Core
curl http://localhost:3000                 # Chat UI
curl http://localhost:5001/health          # Calculations Agent
curl http://localhost:5002/health          # Content Management
curl http://localhost:5003/health          # Web Search
curl http://localhost:8050/health          # Python MCP
curl http://localhost:8051/health          # DDG MCP
```

### Logs Location

```bash
# Docker service logs
docker-compose logs [service-name]

# DIAL Core logs
ls -la ./core-logs/

# Agent logs (stdout)
# View in terminal where agent is running
```

## IDE Setup

### VS Code

Recommended extensions:
- Python
- Docker
- YAML

`.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/dial_mas_mesh/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true
}
```

### PyCharm

1. Set Python interpreter: `dial_mas_mesh/bin/python`
2. Mark `task` as Sources Root
3. Enable Docker integration
4. Configure run configurations for each agent

---

*Last updated: 2025-12-31 | Version: 1.0.0*
