from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
import os

from app.services import OpenAIService

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"

class Message(BaseModel):
    """Message model for chat."""
    role: str
    content: str

class ChatRequest(BaseModel):
    """Chat request model."""
    messages: List[Message]

settings = Settings()

app = FastAPI(
    title="GenCommAI API",
    description="API for GenCommAI project",
    version="0.1.0",
    debug=settings.debug,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency for OpenAI service
def get_openai_service() -> OpenAIService:
    """Get OpenAI service instance."""
    return OpenAIService()  # Will use defaults: gpt-4, temperature=0.0, max_tokens=None

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to GenCommAI API"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Example endpoint using OpenAI service
@app.post("/chat")
async def chat(
    request: ChatRequest,
    openai_service: OpenAIService = Depends(get_openai_service),
):
    """Chat endpoint using OpenAI."""
    # Convert Pydantic models to dictionaries
    messages = [msg.model_dump() for msg in request.messages]
    response = openai_service.create_chat_completion(messages)
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    ) 