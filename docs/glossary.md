---
title: Glossary - AI DIAL MAS Mesh
description: Domain terms, abbreviations, and technical vocabulary
version: 1.0.0
last_updated: 2025-12-31
related: [README.md, architecture.md]
tags: [glossary, terminology, definitions]
---

# Glossary

## A

**Agent**  
An autonomous AI system specialized in a specific domain (calculations, content management, or web search) that can use tools and communicate with other agents.

**Agent Tool**  
A tool that allows one agent to call another agent as part of its workflow. Implements peer-to-peer communication.

**API Key**  
Authentication credential required to access DIAL services and upstream AI models.

**Async/Await**  
Python asynchronous programming pattern used throughout the codebase for non-blocking I/O operations.

**AsyncDial**  
Asynchronous client from aidial-client library for making streaming API calls to DIAL endpoints.

**Attachment**  
A file or resource associated with a message, such as PDFs, images, or generated charts.

## B

**BaseAgent**  
Abstract base class providing core orchestration logic for all agents in the system.

**BaseTool**  
Abstract base class defining the interface for all tools (simple tools, MCP tools, agent tools).

## C

**Calculations Agent**  
Specialized agent for mathematical operations, Python code execution, and chart generation. Runs on port 5001.

**Chat Completion**  
The process of generating AI responses to user messages, following OpenAI's API pattern.

**Choice**  
A response option in streaming chat completions, containing content, tool calls, and custom metadata.

**Content Management Agent**  
Specialized agent for file extraction and RAG-based semantic search. Runs on port 5002.

**Custom Content**  
Extended metadata in messages containing state, attachments, and stages beyond standard OpenAI format.

## D

**DIAL (Distributed Inference and AI Layer)**  
The platform providing API gateway, routing, and orchestration for AI models and applications.

**DIAL Core**  
Central gateway service routing requests between clients and agents/models. Runs on port 8080.

**DIAL Unified Protocol**  
OpenAI-compatible protocol allowing applications to communicate like they communicate with AI models.

**Deployment Name**  
Unique identifier for an agent or model in DIAL Core configuration (e.g., "calculations-agent").

**Docker Compose**  
Tool for defining and running multi-container Docker applications, used to orchestrate all services.

**DuckDuckGo**  
Web search engine integrated via MCP server for Web Search Agent capabilities.

## E

**Endpoint**  
URL where an agent or service exposes its API (e.g., http://localhost:5001/openai/deployments/...).

## F

**FAISS**  
Facebook AI Similarity Search - library used for efficient similarity search in RAG implementation.

**forwardAuthToken**  
Configuration flag indicating that DIAL Core should forward authentication tokens to agents.

## G

**GPT-4o**  
OpenAI's AI model used as the reasoning engine for all agents in the system.

## H

**History Propagation**  
Mode where full conversation context between two agents is shared in subsequent calls (vs. one-shot mode).

**host.docker.internal**  
Special DNS name in Docker that resolves to the host machine's IP address, used for agent communication.

## I

**inputAttachmentTypes**  
Configuration specifying which file types an agent can accept (PDF, CSV, TXT, HTML).

## M

**MAS (Multi-Agent System)**  
Architecture where multiple autonomous agents collaborate to solve complex problems.

**MCP (Model Context Protocol)**  
Protocol for integrating external tools and services, used for Python interpreter and web search.

**Mesh Architecture**  
Design pattern where agents can call each other directly in a peer-to-peer manner, forming a network.

**Message**  
Unit of conversation containing role (user/assistant/tool), content, and optional metadata.

## O

**One-Shot Mode**  
Communication mode where only a single prompt is sent to an agent without prior conversation context.

## P

**P2P (Peer-to-Peer)**  
Direct communication between agents without central coordination, forming a mesh network.

**P2P History**  
Conversation history maintained separately for each pair of agents that communicate.

**Pagination**  
Technique for handling large content by splitting it into pages (used in file extraction).

**Plotly**  
Python library for creating interactive visualizations, used for chart generation.

**Prompt**  
Text instruction or question sent to an AI model or agent.

**Python Interpreter MCP**  
External service providing sandboxed Python code execution capabilities. Runs on port 8050.

## R

**RAG (Retrieval-Augmented Generation)**  
Technique combining semantic search over documents with AI generation for question answering.

**Redis**  
In-memory data store used by DIAL Core for caching and session management.

**Role**  
Message attribute indicating sender type: `user`, `assistant`, `system`, or `tool`.

## S

**Semantic Search**  
Search technique using meaning and context rather than exact keyword matching.

**Sentence Transformers**  
Library for generating text embeddings used in RAG semantic search.

**Stage**  
Progress indicator showing intermediate steps in agent/tool execution, supporting nested stages.

**Stage Propagation**  
Process of passing nested stages from called agents back to calling agents for visibility.

**State**  
Persistent data structure in messages containing tool call history and agent-specific context.

**Streaming**  
Real-time delivery of response chunks as they're generated, providing immediate feedback.

**System Prompt**  
Initial instructions defining an agent's role, capabilities, and behavior patterns.

## T

**Tool**  
Capability that agents can invoke to perform specific tasks (calculations, searches, code execution).

**Tool Call**  
Request from an AI model to execute a specific tool with given parameters.

**Tool Call History**  
Record of all tool invocations and responses in a conversation, stored in message state.

**Tool Message**  
Response message from a tool execution, containing results and metadata.

**Tool Schema**  
JSON specification describing a tool's name, description, and parameters for AI model understanding.

## U

**Unified Protocol**  
See DIAL Unified Protocol.

**Upstream**  
External AI model service (like OpenAI) that DIAL Core routes requests to.

**Uvicorn**  
ASGI web server used to run agent FastAPI applications.

## W

**Web Search Agent**  
Specialized agent for web research via DuckDuckGo. Runs on port 5003.

## Acronyms

| Acronym | Full Form | Context |
|---------|-----------|---------|
| ADR | Architecture Decision Record | Documentation |
| API | Application Programming Interface | Integration |
| ASGI | Asynchronous Server Gateway Interface | Web Server |
| CLI | Command Line Interface | Development |
| CPU | Central Processing Unit | Resources |
| CSV | Comma-Separated Values | File Format |
| DDG | DuckDuckGo | Web Search |
| DIAL | Distributed Inference and AI Layer | Platform |
| DNS | Domain Name System | Networking |
| ER | Entity-Relationship | Diagrams |
| HTML | HyperText Markup Language | File Format |
| HTTP | HyperText Transfer Protocol | Communication |
| JSON | JavaScript Object Notation | Data Format |
| MAS | Multi-Agent System | Architecture |
| MCP | Model Context Protocol | Tool Integration |
| MIME | Multipurpose Internet Mail Extensions | File Types |
| P2P | Peer-to-Peer | Communication |
| PDF | Portable Document Format | File Format |
| RAG | Retrieval-Augmented Generation | AI Technique |
| REST | Representational State Transfer | API Style |
| SDK | Software Development Kit | Library |
| TXT | Text | File Format |
| UI | User Interface | Frontend |
| URL | Uniform Resource Locator | Addressing |
| YAML | YAML Ain't Markup Language | Configuration |

## Technical Terms by Category

### Agent Architecture
- Base Agent
- Agent Tool
- Mesh Network
- P2P Communication
- Tool Orchestration

### Communication
- DIAL Unified Protocol
- Streaming
- Message Format
- Custom Content
- State Management

### Tools
- Simple Tool
- MCP Tool
- Agent Tool
- Tool Schema
- Tool Call Params

### Data Processing
- RAG Search
- Semantic Search
- Embeddings
- Vector Store
- Text Chunking

### Infrastructure
- Docker Container
- Service Orchestration
- Port Mapping
- Network Bridge
- Volume Mount

---

*Last updated: 2025-12-31 | Version: 1.0.0*
