---
title: ADR-002 - DIAL Unified Protocol for Agent Communication
status: Accepted
date: 2025-12-31
decision_makers: Development Team
---

# ADR-002: DIAL Unified Protocol for Agent Communication

## Status
**Accepted** - 2025-12-31

## Context

Agents in our mesh architecture need to communicate with each other. We must decide on the communication protocol and message format for agent-to-agent calls.

### Requirements

- Agents should call each other like calling AI models
- Support streaming responses
- Maintain conversation context across calls
- Enable custom metadata (state, attachments, stages)
- Leverage existing infrastructure (DIAL Core)
- Be compatible with standard tooling

### Options Considered

1. **Custom RPC Protocol**: Design proprietary protocol for agent communication
2. **gRPC**: Use Google's RPC framework
3. **GraphQL**: Query language for API
4. **REST API**: Custom REST endpoints
5. **DIAL Unified Protocol**: OpenAI-compatible protocol via DIAL

## Decision

Use **DIAL Unified Protocol** (OpenAI-compatible `/chat/completions` endpoint) for all agent-to-agent communication.

## Rationale

### Key Advantages

**Protocol Consistency**
```python
# Same pattern for model calls and agent calls
async with AsyncDial(...) as client:
    stream = await client.chat_completions_stream(
        deployment_id="gpt-4o",  # or "calculations-agent"
        messages=[...],
        tools=[...]
    )
```
- Developers use familiar OpenAI API patterns
- No need to learn new protocols
- Code reuse between model and agent calls

**Infrastructure Leverage**
- DIAL Core handles routing, authentication, caching
- Existing monitoring and logging work automatically
- No additional infrastructure required
- Rate limiting and access control built-in

**Context Management**
- Calling application provides full message history
- Standard OpenAI message format
- Extensions via `custom_content` field
- Tool calls follow OpenAI schema

**Streaming Support**
- Real-time response chunks
- Server-Sent Events (SSE) protocol
- Progress indication via stages
- Efficient for long-running operations

**Extensibility**
- `custom_content` allows arbitrary metadata
- Stages for nested progress tracking
- Attachments for file passing
- State preservation for P2P history

### Implementation Pattern

```python
# Agent Tool executing another agent
async def _execute(self, tool_call_params: ToolCallParams) -> Message:
    # Parse arguments
    args = json.loads(tool_call_params.tool_call.function.arguments)
    prompt = args["prompt"]
    
    # Prepare messages with context
    messages = self._prepare_messages(tool_call_params)
    
    # Call via DIAL Unified Protocol
    async with AsyncDial(
        base_url=self.endpoint,
        api_key=tool_call_params.api_key,
        api_version='2025-01-01-preview'  # Streaming support
    ) as client:
        stream = await client.chat_completions_stream(
            deployment_id=self.deployment_name,
            messages=messages,
            extra_headers={"x-conversation-id": tool_call_params.conversation_id}
        )
        
        # Stream response, propagate stages
        async for chunk in stream:
            # Process chunks...
            pass
```

## Trade-offs

### Advantages

✅ **No Learning Curve**: Developers already know OpenAI API  
✅ **Tooling Compatibility**: Works with existing OpenAI-compatible tools  
✅ **Infrastructure Reuse**: DIAL Core handles complexity  
✅ **Future-Proof**: OpenAI API is industry standard  
✅ **Debugging**: Standard HTTP tools work out of the box

### Disadvantages

❌ **OpenAI API Constraints**: Limited to OpenAI's message format  
  *Mitigation: Use custom_content for extensions*

❌ **Overhead**: JSON serialization for every call  
  *Acceptable: Benefit of standard format outweighs cost*

❌ **Streaming Complexity**: SSE protocol requires careful handling  
  *Mitigated: aidial-client library handles it*

❌ **Not Optimized for Agent-Specific Cases**: Generic protocol  
  *Acceptable: Flexibility more valuable than optimization*

## Alternatives Considered

### 1. Custom RPC Protocol

**Pros:**
- Optimized for our specific needs
- Binary format (faster)
- Custom features without constraints

**Cons:**
- Reinventing the wheel
- No tooling ecosystem
- High maintenance burden
- Steep learning curve

**Why Rejected:** Benefits don't justify development cost

### 2. gRPC

**Pros:**
- High performance (binary protocol)
- Strong typing with protobuf
- Built-in streaming
- Good tooling support

**Cons:**
- Different paradigm from DIAL
- Requires protobuf definitions
- Not compatible with DIAL Core
- Separate infrastructure needed

**Why Rejected:** Doesn't integrate with DIAL ecosystem

### 3. GraphQL

**Pros:**
- Flexible query language
- Client specifies data needs
- Good for complex queries

**Cons:**
- Not designed for streaming conversations
- Complex schema management
- Over-engineering for our use case

**Why Rejected:** Not suitable for conversation-based interactions

### 4. Custom REST API

**Pros:**
- Simple HTTP endpoints
- Flexible design
- Wide tool support

**Cons:**
- Need to design custom message format
- Streaming requires SSE or WebSockets
- No standardization
- More code to maintain

**Why Rejected:** DIAL Unified Protocol gives us all REST benefits plus standardization

## Implementation Details

### Message Format

Standard OpenAI with extensions:

```typescript
{
  role: "user" | "assistant" | "tool" | "system",
  content: string,
  tool_calls?: ToolCall[],
  custom_content?: {
    state?: {
      tool_call_history: any[],
      [agent_name: string]: any
    },
    attachments?: Attachment[],
    stages?: Stage[]
  }
}
```

### Endpoints

All agents expose:
```
POST /openai/deployments/{deployment_name}/chat/completions
```

### Headers

```
Authorization: Bearer {api_key}
Content-Type: application/json
x-conversation-id: {uuid}
```

### Streaming Protocol

Server-Sent Events (SSE):
```
data: {"choices":[{"delta":{"content":"Hello"}}]}

data: {"choices":[{"delta":{"content":" world"}}]}

data: [DONE]
```

## Consequences

### Positive

- Immediate developer productivity (familiar API)
- Strong ecosystem of tools and libraries
- Future compatibility with OpenAI ecosystem
- Easy integration with DIAL infrastructure
- Standard debugging and monitoring tools work

### Negative

- Bound to OpenAI API evolution
- Custom extensions may not be portable
- JSON overhead vs. binary protocols
- Limited to HTTP/SSE (no WebSocket alternative in standard)

### Mitigation Strategies

1. **API Version Locking**: Use api_version parameter for stability
2. **Custom Content Extensions**: Structured extensions for our needs
3. **Abstraction Layer**: BaseAgentTool hides protocol details
4. **Documentation**: Clear guidance on standard vs. custom fields

## Validation

### Success Criteria

- [x] Agent-to-agent calls work via standard OpenAI client
- [x] Streaming responses propagate correctly
- [x] Custom content (state, stages) transmitted successfully
- [x] DIAL Core routes requests properly
- [x] Authentication tokens forwarded correctly

### Monitoring

- Request/response logs follow OpenAI format
- Standard HTTP monitoring tools work
- Performance metrics via standard endpoints
- Error rates tracked like model calls

## References

- [OpenAI Chat Completions API](https://platform.openai.com/docs/api-reference/chat)
- [DIAL Unified Protocol Specification](https://docs.epam-rail.com)
- [Server-Sent Events (SSE) Standard](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [aidial-client Documentation](https://github.com/epam/ai-dial-client)

## Notes

- This decision makes agent development accessible to anyone familiar with OpenAI API
- Custom extensions (custom_content) provide flexibility within standard framework
- Future consideration: Evaluate if binary protocol layer needed for performance

---

*Status: Accepted | Last Updated: 2025-12-31*
