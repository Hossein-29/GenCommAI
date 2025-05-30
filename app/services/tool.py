"""Tool definitions and implementations for agents."""

from dataclasses import dataclass
from typing import Callable, Dict, Any, Optional, Union, Literal

@dataclass
class Tool:
    """Data class representing a tool that can be used by an agent.
    
    For function tools, follows OpenAI's exact format:
    {
        "type": "function",
        "function": {
            "name": str,
            "description": str,
            "parameters": Dict[str, Any]
        }
    }
    
    For built-in tools like web_search_preview:
    {
        "type": "web_search_preview"
    }
    """
    type: Union[Literal["function"], Literal["web_search_preview"]]
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    function: Optional[Callable] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the tool to OpenAI's tool format."""
        if self.type == "function":
            return {
                "type": "function",
                "function": {
                    "name": self.name,
                    "description": self.description,
                    "parameters": self.parameters
                }
            }
        elif self.type == "web_search_preview":
            return {"type": "web_search_preview"}
        return {"type": self.type}
