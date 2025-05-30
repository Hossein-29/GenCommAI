"""Base agent implementation with tool support."""

from typing import List, Dict, Any, Optional
from app.services.openai_service import OpenAIService
from app.services.tool import Tool

class Agent:
    """Agent that can use tools in conversations with OpenAI."""

    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        system_message: str = "You are a helpful AI assistant that can use tools to help users.",
        tools: Optional[List[Tool]] = None,
    ):
        """Initialize the agent.
        
        Args:
            model: The OpenAI model to use.
            temperature: Temperature for completions.
            max_tokens: Maximum tokens for completions.
            system_message: The system message to use for the agent's personality.
            tools: Optional list of tools to register on initialization.
        """
        self.service = OpenAIService(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        self.system_message = system_message
        self.conversation_history: List[Dict[str, str]] = [
            {"role": "system", "content": system_message}
        ]
        
        # Register any tools provided during initialization
        if tools:
            for tool in tools:
                self.register_tool(tool)

    def register_tool(self, tool: Tool) -> None:
        """Register a tool that the agent can use.
        
        Args:
            tool: A Tool instance containing the tool definition.
        """
        tool_dict = tool.to_dict()
        if tool.type == "function" and tool.function is not None:
            # Register the function with the service
            self.service.register_function(
                name=tool.name,  # Use the explicit name from the tool
                function=tool.function,
                description=tool.description or "",
                parameters=tool.parameters or {},
            )
        # Add the tool definition to the service
        self.service.tool_definitions.append(tool_dict)

    def chat(
        self,
        message: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Have a conversation with the agent.
        
        Args:
            message: The user's message.
            temperature: Optional override for temperature.
            max_tokens: Optional override for max tokens.
            
        Returns:
            The agent's response.
        """
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Get response from OpenAI
        response = self.service.create_chat_completion_with_tools(
            messages=self.conversation_history,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        # Extract assistant's message
        assistant_message = response["choices"][0]["message"]
        
        # Add assistant's message to conversation history
        self.conversation_history.append(assistant_message)
        
        # Return the content of the assistant's message
        return assistant_message.get("content", "")

    def reset_conversation(self) -> None:
        """Reset the conversation history while keeping the system message."""
        self.conversation_history = [
            {"role": "system", "content": self.system_message}
        ]