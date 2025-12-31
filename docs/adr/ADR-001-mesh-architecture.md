---
title: ADR-001 - Mesh Architecture Selection
status: Accepted
date: 2025-12-31
decision_makers: Development Team
---

# ADR-001: Mesh Architecture Selection

## Status
**Accepted** - 2025-12-31

## Context

We need to design a multi-agent system where specialized agents (Calculations, Content Management, Web Search) can collaborate to solve complex tasks. Several architectural patterns were considered:

1. **Centralized Orchestrator**: Single coordinator agent managing all interactions
2. **Hierarchical**: Tree-like structure with parent-child relationships
3. **Mesh/P2P**: Agents call each other directly as tools
4. **Event-Driven**: Message bus with publish-subscribe pattern

### Key Requirements

- Agents must be able to collaborate on complex tasks
- Each agent specializes in a specific domain
- System should be extensible to add new agents
- Communication should be efficient and maintainable
- Context management must be clear and trackable

## Decision

We chose **Mesh/Peer-to-Peer Architecture** where each agent can call any other agent directly as a tool.

### Architecture Principles

1. **Agents as Tools**: Other agents are exposed as tools in each agent's toolset
2. **Context Ownership**: The calling agent manages conversation context
3. **Protocol Unification**: All communication uses DIAL Unified Protocol (OpenAI-compatible)
4. **Stateless Agents**: Agents don't maintain session state; context passed in each request
5. **P2P History**: Separate conversation history maintained per agent pair

## Rationale

### Advantages

**Flexibility**
- Agents can collaborate in any combination needed for the task
- No bottleneck at central orchestrator
- Easy to add new agents to the mesh

**Simplicity**
- Each agent uses the same tool interface regardless of whether calling a simple tool or another agent
- No complex message routing or event handling
- Clear ownership of context (calling agent provides it)

**Protocol Consistency**
- Agent-to-agent calls use the same protocol as model API calls
- Leverages existing DIAL infrastructure
- Familiar OpenAI-compatible patterns

**Scalability**
- Agents can run independently on different machines/ports
- Parallel tool execution reduces latency
- No single point of failure

### Trade-offs

**Cyclic Dependencies Risk**
- Agents can theoretically call each other in infinite loops
- Mitigated by: Model intelligence, context limits, timeout mechanisms

**Context Management Complexity**
- Calling agent must manage conversation history
- Mitigated by: BaseAgent handles this automatically, clear P2P history structure

**No Global Coordination**
- Can't easily enforce system-wide policies or priorities
- Acceptable for current use cases; agents self-coordinate through model reasoning

## Implementation

### Agent Communication

```python
# Agent A calls Agent B as a tool
class AgentATool(BaseAgentTool):
    deployment_name = "agent-b"
    
    async def _execute(self, tool_call_params):
        # Prepare messages (one-shot or with P2P history)
        messages = self._prepare_messages(tool_call_params)
        
        # Call Agent B via DIAL protocol
        async with AsyncDial(...) as client:
            stream = await client.chat_completions_stream(
                deployment_id=self.deployment_name,
                messages=messages
            )
            # Stream response, propagate stages
            ...
```

### P2P History Structure

```json
{
  "state": {
    "tool_call_history": [...],  // Current agent's history
    "agent_b_name": {             // P2P history with Agent B
      "tool_call_history": [...]
    }
  }
}
```

## Alternatives Considered

### 1. Centralized Orchestrator

**Pros:**
- Global view of system state
- Easy to implement system-wide policies
- Simpler deadlock prevention

**Cons:**
- Single point of failure
- Bottleneck for all agent interactions
- More complex orchestration logic
- Harder to scale

**Why Rejected:** Doesn't align with DIAL's decentralized design philosophy

### 2. Hierarchical Structure

**Pros:**
- Clear parent-child relationships
- Natural task decomposition
- Well-understood pattern

**Cons:**
- Rigid structure limits flexibility
- Agents can't collaborate across branches
- Harder to determine optimal hierarchy

**Why Rejected:** Too restrictive for our dynamic collaboration needs

### 3. Event-Driven Message Bus

**Pros:**
- Loose coupling between agents
- Asynchronous communication
- Easy to add new subscribers

**Cons:**
- Requires additional infrastructure (message broker)
- Harder to track request-response flows
- More complex debugging
- Not aligned with DIAL's synchronous streaming model

**Why Rejected:** Adds unnecessary complexity for current requirements

## Consequences

### Positive

- **Extensibility**: New agents can be added by simply implementing agent tool wrappers
- **Developer Experience**: Familiar patterns (OpenAI API) make development intuitive
- **Debugging**: Clear request-response traces through stages and logs
- **Performance**: Parallel tool execution possible within each agent
- **Infrastructure**: Leverages existing DIAL Core for routing and authentication

### Negative

- **Context Size**: P2P histories can grow large with many interactions
  - Mitigation: Future enhancement for history compression
- **Circular Dependency Management**: Relies on model intelligence to avoid loops
  - Mitigation: Monitor conversation lengths, add safeguards if needed
- **No Global State**: Can't easily coordinate between unrelated agent pairs
  - Mitigation: Not a current requirement; can add if needed

### Neutral

- **Learning Curve**: Developers must understand P2P communication patterns
- **Testing Complexity**: Integration tests require multiple agents running

## Monitoring and Validation

### Success Metrics

- Agent-to-agent calls complete successfully
- P2P history correctly preserved across interactions
- No circular dependency issues in production
- Agent collaboration achieves task goals efficiently

### Evaluation Criteria

- [ ] Weather chart scenario completes end-to-end
- [ ] PDF Q&A scenario works with file extraction
- [ ] Multi-agent collaboration traces are clear in logs
- [ ] System handles 10+ concurrent agent-to-agent calls
- [ ] Context size remains manageable (< 50K tokens per conversation)

## References

- [DIAL Unified Protocol Documentation](https://docs.epam-rail.com)
- [OpenAI Chat Completions API](https://platform.openai.com/docs/api-reference/chat)
- [Multi-Agent System Design Patterns](https://www.researchgate.net/publication/multi-agent-patterns)

## Notes

- This decision was driven by DIAL's architecture and existing infrastructure
- Future enhancement: Add agent capability negotiation protocol
- Consider revisiting if system scales beyond 10 agents

---

*Status: Accepted | Last Updated: 2025-12-31*
