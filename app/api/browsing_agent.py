"""API endpoints for the browsing agent."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import traceback
import logging
from app.services import Agent
from app.services.tool import Tool
from app.services.openai_service import OpenAIService
from system_prompt import system_prompt
from app.TopicAgent.ProductTopic import ProductClassifierAgent
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["agent"])

def web_search_tool(query: str) -> str:
    """Tool function that performs a web search using OpenAI's web search capabilities."""
    service = OpenAIService()
    response = service.create_web_search_response(input_text=query)
    print(response)

    # Extract web search results if available
    web_search_results = response.get("web_search_call", {}).get("results", [])
    if web_search_results:
        results_text = "\n\nWeb Search Results:\n"
        for result in web_search_results:
            results_text += f"- {result.get('title', '')}: {result.get('snippet', '')}\n"
        return results_text
    
    # Fallback to output text if no specific results
    return response.get("output_text", "")

# Define the browsing tool
browsing_tool = Tool(
    type="function",
    name="web_search",
    description="Search the web for current information about a topic",
    function=web_search_tool,
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to look up on the web"
            }
        },
        "required": ["query"]
    }
)



# Initialize the browsing agent
browsing_agent = Agent(
    model="gpt-4.1",
    tools=[browsing_tool],
    system_message=system_prompt
)

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None

class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Chat with the browsing agent.
    
    Args:
        request: The chat request containing the message and optional parameters.
        
    Returns:
        The agent's response.
        
    Raises:
        HTTPException: If there's an error processing the request.
    """
    product_name_normalizer = ProductClassifierAgent()
    brand_model = product_name_normalizer.run(request.message)  
    print(brand_model)
    # brand_model = agent.run("ایسوس ویوو بوک ۱۵ ")
    # print(brand_model)
    try:
        logger.info(f"Received chat request: {brand_model}")
        response = browsing_agent.chat(
            message=brand_model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        # response = SummarizeAgent(response).run()
        json_response = json.loads(response)
        print(json_response)

        return ChatResponse(response=response)
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error in chat endpoint: {str(e)}\n{error_traceback}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "traceback": error_traceback
            }
        )

@router.post("/reset")
async def reset_conversation() -> dict:
    """Reset the agent's conversation history."""
    try:
        browsing_agent.reset_conversation()
        return {"status": "success", "message": "Conversation history reset"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 