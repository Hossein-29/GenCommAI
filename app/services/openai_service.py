"""OpenAI service for handling OpenAI API interactions."""

from typing import Optional, Dict, Any, Callable, List, Union
import os
import json
from openai import OpenAI
from pydantic import BaseModel
from search_prompt import search_prompt

class OpenAIConfig(BaseModel):
    """OpenAI configuration settings."""
    api_key: str
    model: str = "gpt-4"
    temperature: float = 0.0
    max_tokens: Optional[int] = None

class OpenAIService:
    """Service for interacting with OpenAI API."""

    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
    ):
        """Initialize the OpenAI service.
        
        Args:
            model: The OpenAI model to use.
            temperature: Temperature for completions.
            max_tokens: Maximum tokens for completions.
        """
        api_key = os.getenv("METIS_OPENAI_KEY", "")
        if not api_key:
            raise ValueError("METIS_OPENAI_KEY environment variable is not set")
            
        self.config = OpenAIConfig(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        self.client = OpenAI(api_key=self.config.api_key, base_url=os.getenv("METIS_BASE_URL", "https://api.openai.com/v1"))
        self.registered_functions: Dict[str, Callable] = {}
        self.tool_definitions: List[Dict[str, Any]] = []

    def register_function(
        self,
        name: str,
        function: Callable,
        description: str,
        parameters: Dict[str, Any],
    ) -> None:
        """Register a function that can be called by the model.
        
        Args:
            name: Name of the function.
            function: The actual Python function to call.
            description: Description of what the function does.
            parameters: JSON Schema of the function parameters.
            
        Example:
            def get_weather(location: str) -> str:
                return f"Weather in {location}"
                
            service.register_function(
                name="get_weather",
                function=get_weather,
                description="Get the weather for a location",
                parameters={
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city to get weather for"
                        }
                    },
                    "required": ["location"]
                }
            )
        """
        self.registered_functions[name] = function
        self.tool_definitions.append({
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        })

    def _execute_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call and return the result.
        
        Args:
            tool_call: The tool call from the model's response.
            
        Returns:
            Dictionary containing the tool call result.
        """
        function_name = tool_call["function"]["name"]
        function_args = json.loads(tool_call["function"]["arguments"])
        
        print(f"\n🤖 Executing tool: {function_name}")
        print(f"📝 Arguments: {function_args}")
        
        if function_name not in self.registered_functions:
            raise ValueError(f"Function {function_name} is not registered")
            
        function = self.registered_functions[function_name]
        result = function(**function_args)
        print(f"✅ Result: {result}\n")
        
        return {
            "tool_call_id": tool_call["id"],
            "role": "tool",
            "name": function_name,
            "content": str(result)
        }

    def create_chat_completion(
        self,
        messages: list[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a chat completion.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            temperature: Optional override for temperature.
            max_tokens: Optional override for max tokens.
            
        Returns:
            The chat completion response.
        """
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=temperature or self.config.temperature,
            max_tokens=max_tokens or self.config.max_tokens,
        )
        return response.model_dump()


    def create_chat_completion_with_tools(
        self,
        messages: list[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        max_iterations: int = 5,
    ) -> Dict[str, Any]:
        """Create a chat completion with tools support and handle tool execution."""
        if not self.tool_definitions:
            raise ValueError("No functions registered. Use register_function() first.")
            
        print("\n🔄 Starting conversation with tools")
        print(f"📋 Available tools: {[tool for tool in self.tool_definitions]}")
        
        current_messages = messages.copy()
        iterations = 0
        
        while iterations < max_iterations:
            try:
                print(f"\n📝 Iteration {iterations + 1}/{max_iterations}")
                
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=current_messages,
                    tools=self.tool_definitions,
                    tool_choice="auto",
                    temperature=temperature or self.config.temperature,
                    max_tokens=max_tokens or self.config.max_tokens,
                )
                response_dict = response.model_dump()
                
                # Get the assistant's message
                assistant_message = response_dict["choices"][0]["message"]
                print(f"💭 Assistant: {assistant_message.get('content', '')}")
                
                current_messages.append(assistant_message)
                
                # If there are no tool calls, we're done
                if not assistant_message.get("tool_calls"):
                    print("✨ Conversation complete\n")
                    return response_dict
                    
                # Execute all tool calls
                tool_calls = assistant_message.get("tool_calls", [])
                print(f"🔧 Executing {len(tool_calls)} tool calls")
                
                for tool_call in tool_calls:
                    # Handle function tools
                    tool_result = self._execute_tool_call(tool_call)
                    current_messages.append(tool_result)
                    
                iterations += 1
                
            except Exception as e:
                print(f"\n❌ Error in iteration {iterations + 1}:")
                print(f"Error type: {type(e).__name__}")
                print(f"Error message: {str(e)}")
                import traceback
                print(f"Traceback:\n{traceback.format_exc()}")
                raise
                
        print("❌ Maximum iterations exceeded\n")
        raise RuntimeError(f"Maximum number of iterations ({max_iterations}) exceeded")

    def create_web_search_response(
        self,
        input_text: str,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Create a response using web search.
        
        Args:
            input_text: The input text to search for.
            temperature: Optional override for temperature.
            
        Returns:
            The response from the model.
        """
        print("\n🔄 Starting web search response")
        print(f"📝 Input: {input_text}")

        
        response = self.client.responses.create(
            model="gpt-4.1-mini",
            tools=[{"type": "web_search_preview"}],
            include=["web_search_call.results"],
            input=f"{search_prompt}{input_text}",
            temperature=temperature or self.config.temperature,
        )
        return response.model_dump()
