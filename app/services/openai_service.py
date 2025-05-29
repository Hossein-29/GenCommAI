"""OpenAI service for handling OpenAI API interactions."""

from typing import Optional, Dict, Any
import os
from openai import OpenAI
from pydantic import BaseModel

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
