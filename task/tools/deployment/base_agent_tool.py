import json
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any

from aidial_client import AsyncDial
from aidial_sdk.chat_completion import Message, Role, CustomContent, Stage, Attachment
from pydantic import StrictStr

from task.tools.base_tool import BaseTool
from task.tools.models import ToolCallParams
from task.utils.stage import StageProcessor


class BaseAgentTool(BaseTool, ABC):

    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    @property
    @abstractmethod
    def deployment_name(self) -> str:
        pass

    async def _execute(self, tool_call_params: ToolCallParams) -> str | Message:
        """
        Executes agent-to-agent communication via DIAL Unified Protocol.
        
        Flow:
        1. Parse prompt and propagate_history from tool call arguments
        2. Prepare message history via _prepare_messages (one-shot or full P2P context)
        3. Stream response from called agent using AsyncDial client
        4. Propagate stages and attachments from agent response to calling agent
        5. Collect state for P2P history preservation
        6. Return Tool message with collected content and custom_content
        
        Args:
            tool_call_params: Contains tool_call with function arguments, stage for streaming,
                            choice for stage/attachment propagation, API key, conversation_id
        
        Returns:
            Message with tool_call_id, collected content, and custom_content containing state
        """
        # Parse tool call arguments (prompt is required, propagate_history is optional)
        args = json.loads(tool_call_params.tool_call.function.arguments)
        
        # Prepare messages for the called agent (one-shot or full P2P history)
        messages = self._prepare_messages(tool_call_params)
        
        # Initialize AsyncDial client with streaming support (api_version enables streaming protocol)
        async with AsyncDial(
            base_url=self.endpoint,
            api_key=tool_call_params.api_key,
            api_version='2025-01-01-preview'
        ) as client:
            # Stream response from called agent with conversation context
            stream = await client.chat_completions_stream(
                deployment_id=self.deployment_name,
                messages=messages,
                extra_headers={"x-conversation-id": tool_call_params.conversation_id}
            )
            
            # Initialize collection variables for agent response
            content = ''  # Accumulated text content from agent
            custom_content = CustomContent()  # State and attachments from agent response
            stages_map: dict[int, Stage] = {}  # Track propagated stages by their index
            
            # Stream chunks from called agent, propagating progress to calling agent
            async for chunk in stream:
                # Extract first choice from chunk (agent responses contain single choice)
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    
                    # Stream content to this tool call's stage for real-time visibility
                    if delta.content:
                        content += delta.content
                        tool_call_params.stage.append_content(delta.content)
                    
                    # Propagate custom content (state, attachments, stages) from called agent
                    if delta.custom_content:
                        response_custom = delta.custom_content
                        
                        # Preserve state for P2P history (enables history propagation in future calls)
                        if response_custom.state:
                            custom_content.state = response_custom.state
                        
                        # Propagate attachments to calling agent's choice (e.g., generated charts)
                        if response_custom.attachments:
                            for attachment in response_custom.attachments:
                                tool_call_params.choice.add_attachment(**attachment.dict(exclude_none=True))
                        
                        # Propagate nested stages from called agent for multi-level visibility
                        if response_custom.stages:
                            custom_dict = response_custom.dict(exclude_none=True)
                            stages_data = custom_dict.get('stages', [])
                            
                            for stage_data in stages_data:
                                stage_index = stage_data.get('index')
                                
                                # Create or update propagated stage by index
                                if stage_index not in stages_map:
                                    # Create new propagated stage with name from response
                                    propagated_stage = StageProcessor.open_stage(
                                        tool_call_params.choice,
                                        stage_data.get('name')
                                    )
                                    stages_map[stage_index] = propagated_stage
                                else:
                                    propagated_stage = stages_map[stage_index]
                                
                                # Update propagated stage name if changed
                                if stage_data.get('name'):
                                    propagated_stage.name = stage_data.get('name')
                                
                                # Stream content to propagated stage
                                if stage_data.get('content'):
                                    propagated_stage.append_content(stage_data.get('content'))
                                
                                # Propagate attachments to nested stage
                                if stage_data.get('attachments'):
                                    for attachment in stage_data['attachments']:
                                        propagated_stage.add_attachment(**attachment)
                                
                                # Close propagated stage when response stage completes
                                if stage_data.get('status') == 'completed':
                                    StageProcessor.close_stage_safely(propagated_stage)
        
        # Ensure all propagated stages are closed (cleanup for any missed closures)
        for propagated_stage in stages_map.values():
            StageProcessor.close_stage_safely(propagated_stage)
        
        # Return Tool message with collected content and state for history preservation
        return Message(
            role=Role.TOOL,
            content=content,
            tool_call_id=tool_call_params.tool_call.id,
            custom_content=custom_content
        )

    def _prepare_messages(self, tool_call_params: ToolCallParams) -> list[dict[str, Any]]:
        """
        Prepares message history for the called agent based on propagate_history mode.
        
        Two modes:
        1. One-shot (propagate_history=false): Single user message with prompt only
        2. Full P2P context (propagate_history=true): Extract and propagate all historical
           interactions between calling agent and called agent from assistant message states
        
        Flow:
        1. Parse prompt and propagate_history from tool call arguments
        2. If one-shot mode: return single user message with prompt
        3. If P2P mode: iterate through request messages, extract P2P history from assistant
           message states (key = self.name), refactor state to preserve only relevant history
        4. Append current user message with prompt and custom_content (for attachments)
        
        Args:
            tool_call_params: Contains messages from request, tool_call with arguments
        
        Returns:
            List of message dicts ready for AsyncDial client (OpenAI-compatible format)
        """
        # Parse tool call arguments
        args = json.loads(tool_call_params.tool_call.function.arguments)
        prompt: str = args["prompt"]
        propagate_history: bool = args.get("propagate_history", False)
        
        messages: list[dict[str, Any]] = []
        
        # Extract P2P history from request messages if propagate_history is enabled
        if propagate_history:
            # Iterate through request messages to find P2P communication history
            for i, message in enumerate(tool_call_params.messages):
                # Process assistant messages with state containing P2P history
                if message.role == Role.ASSISTANT:
                    if message.custom_content and message.custom_content.state:
                        state = message.custom_content.state
                        
                        # Check if state contains history for the agent we're calling (key = self.name)
                        if isinstance(state, dict) and self.name in state:
                            # Extract P2P history from state
                            agent_state = state[self.name]
                            
                            # Add preceding user message (context for this assistant message)
                            if i > 0:
                                prev_message = tool_call_params.messages[i - 1]
                                if prev_message.role == Role.USER:
                                    # Append attachment URLs to user message content
                                    attachments_urls_content = ''
                                    if prev_message.custom_content and prev_message.custom_content.attachments:
                                        attachments_urls_content = '\n\nAttached files URLs:\n'
                                        for attachment in prev_message.custom_content.attachments:
                                            if attachment.url:
                                                attachments_urls_content += f"{attachment.url}\n"
                                            elif attachment.reference_url:
                                                attachments_urls_content += f"{attachment.reference_url}\n"
                                    
                                    content = prev_message.content or ''
                                    if attachments_urls_content:
                                        content += attachments_urls_content
                                    
                                    messages.append({
                                        "role": Role.USER.value,
                                        "content": content
                                    })
                            
                            # Add assistant message with refactored state (only P2P history for called agent)
                            assistant_msg_copy = deepcopy(message)
                            # Refactor state: replace full state with only P2P-specific state
                            assistant_msg_copy.custom_content.state = agent_state
                            messages.append(assistant_msg_copy.dict(exclude_none=True))
        
        # Append current user message with prompt (final request to called agent)
        user_message_dict: dict[str, Any] = {
            "role": Role.USER.value,
            "content": prompt
        }
        
        # Include custom_content if present (for attachment propagation)
        if tool_call_params.messages and tool_call_params.messages[-1].custom_content:
            last_message = tool_call_params.messages[-1]
            if last_message.custom_content:
                user_message_dict["custom_content"] = last_message.custom_content.dict(exclude_none=True)
        
        messages.append(user_message_dict)
        
        return messages