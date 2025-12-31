---
title: Changelog - AI DIAL MAS Mesh
description: Notable changes, releases, and version history
version: 1.0.0
last_updated: 2025-12-31
related: [README.md, roadmap.md]
tags: [changelog, releases, versions]
---

# Changelog

All notable changes to the AI DIAL MAS Mesh project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-31

### Added

#### Core Features
- **Multi-Agent System Implementation**
  - Three specialized agents: Calculations, Content Management, Web Search
  - Peer-to-peer mesh architecture
  - Agent-to-agent communication via DIAL Unified Protocol
  
- **Calculations Agent**
  - Simple calculator tool for basic arithmetic
  - Python code interpreter integration via MCP
  - Chart generation with Plotly
  - Can call Content Management and Web Search agents
  
- **Content Management Agent**
  - File content extraction (PDF, CSV, TXT, HTML)
  - RAG-based semantic search
  - Document pagination support
  - Can call Calculations and Web Search agents
  
- **Web Search Agent**
  - DuckDuckGo search integration via MCP
  - Web page content fetching
  - Research synthesis with citations
  - Can call Calculations and Content Management agents

#### Communication Features
- **P2P History Management**
  - Separate conversation history per agent pair
  - Two modes: one-shot and full history propagation
  - State preservation in message custom_content
  
- **Stage Propagation**
  - Multi-level stage visibility
  - Nested stages from called agents
  - Real-time progress indication
  
- **Attachment Handling**
  - File attachments in requests
  - Generated files (charts, reports) in responses
  - Attachment propagation through agent calls

#### Infrastructure
- **Docker Compose Setup**
  - DIAL Core gateway (port 8080)
  - DIAL Chat UI (port 3000)
  - Redis caching
  - Python Interpreter MCP server (port 8050)
  - DuckDuckGo MCP server (port 8051)
  
- **Agent Applications**
  - FastAPI-based agent servers
  - Uvicorn ASGI server
  - Health check endpoints
  - Configurable ports and endpoints

#### Base Classes & Utilities
- `BaseAgent`: Core orchestration logic
- `BaseTool`: Tool interface and execution
- `BaseAgentTool`: Agent-to-agent communication
- `StageProcessor`: Stage lifecycle management
- `MCPTool`: MCP server tool wrapper
- History unpacking utilities
- Constants and configuration management

#### Documentation
- Comprehensive README with quick start
- Architecture documentation with Mermaid diagrams
- Detailed setup guide
- API reference with schemas
- Testing guide with scenarios
- Glossary of terms
- Architecture Decision Records
- Development roadmap

### Implementation Details

#### File Structure
```
task/
├── agents/
│   ├── base_agent.py (182 lines)
│   ├── calculations/
│   │   ├── calculations_agent.py
│   │   ├── calculations_app.py (92 lines)
│   │   ├── _prompts.py
│   │   └── tools/
│   ├── content_management/
│   │   ├── content_management_agent.py
│   │   ├── content_management_app.py (94 lines)
│   │   ├── _prompts.py
│   │   └── tools/
│   └── web_search/
│       ├── web_search_agent.py
│       ├── web_search_app.py (103 lines)
│       ├── _prompts.py
│       └── tools/
├── tools/
│   ├── base_tool.py
│   ├── deployment/
│   │   ├── base_agent_tool.py (148 lines)
│   │   ├── calculations_agent_tool.py (48 lines)
│   │   ├── content_management_agent_tool.py (48 lines)
│   │   └── web_search_agent_tool.py (48 lines)
│   └── mcp/
└── utils/
    ├── history.py
    ├── stage.py
    └── constants.py
```

#### Dependencies
- aidial-sdk==0.27.0 - DIAL SDK for agent implementation
- aidial-client==0.3.0 - DIAL client for agent-to-agent calls
- mcp==1.20.0 - Model Context Protocol integration
- pydantic==2.12.3 - Data validation
- faiss-cpu==1.12.0 - Vector similarity search
- sentence-transformers==5.1.2 - Text embeddings
- beautifulsoup4==4.14.2 - HTML parsing
- pdfplumber==0.11.7 - PDF extraction
- langchain==1.0.3 - LLM framework
- And more (see requirements.txt)

### Technical Highlights

#### BaseAgentTool Implementation
- `_execute()`: 109 lines of streaming agent communication
- `_prepare_messages()`: 83 lines of history management
- Supports stage propagation with index tracking
- Custom content state preservation
- Error handling and cleanup

#### Agent Applications
- Each agent ~90-100 lines of documented code
- Async tool initialization
- Proper resource management with context managers
- Health check endpoints
- DIALApp integration

### Known Limitations

- No automated test suite (manual testing only)
- P2P history can grow large with many interactions
- No history compression mechanism
- Limited error recovery strategies
- No monitoring/observability built-in

### Configuration Requirements

- DIAL API key must be configured in core/config.json
- Three agent applications in DIAL Core config
- Docker Compose for service orchestration
- Python 3.12+ virtual environment

### Breaking Changes

None (initial release)

## [Unreleased]

### Planned for v1.1.0
- Structured logging with correlation IDs
- Performance metrics collection
- Distributed tracing
- Real-time monitoring dashboard

### Planned for v1.2.0
- Unit test suite (80%+ coverage)
- Integration tests
- CI/CD pipeline
- Automated E2E scenarios

### Planned for v1.3.0
- Multi-modal support
- Enhanced RAG with citations
- History compression
- Agent capability discovery

---

## Version History

| Version | Date | Notes |
|---------|------|-------|
| 1.0.0 | 2025-12-31 | Initial release with 3 agents and P2P mesh |

## Release Notes Format

Each release includes:
- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements

## Semantic Versioning

- **Major (X.0.0)**: Breaking changes
- **Minor (1.X.0)**: New features, backwards compatible
- **Patch (1.0.X)**: Bug fixes, backwards compatible

---

*Last updated: 2025-12-31 | Current Version: 1.0.0*
