#!/usr/bin/env python3
"""
FastAPI REST API for Microsoft Copilot Studio Agent SDK

This provides a REST API interface to interact with your Copilot agent.
Use with Postman, curl, or any HTTP client.

Usage:
    uvicorn api:app --reload --port 8000

Then visit:
    http://localhost:8000/docs  (Swagger UI)
    http://localhost:8000/redoc (ReDoc)

Copyright 2025 AIHQ.ie
Licensed under the Apache License, Version 2.0
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
import asyncio
from datetime import datetime

from copilot_sdk import CopilotAgentClient, CopilotConfig

# Initialize FastAPI app
app = FastAPI(
    title="Copilot Studio Agent API",
    description="REST API for interacting with Microsoft Copilot Studio agents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global client instance (initialized once)
copilot_client: Optional[CopilotAgentClient] = None

# Active conversations storage
conversations: Dict[str, Dict[str, Any]] = {}


# Pydantic Models
class MessageRequest(BaseModel):
    """Request model for sending a message"""
    message: str = Field(..., description="Message to send to the agent", min_length=1)
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID to maintain context")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Hello, how are you?",
                "conversation_id": None
            }
        }


class MessageResponse(BaseModel):
    """Response model for agent messages"""
    response: Any = Field(..., description="Agent's response (can be string or JSON object)")
    conversation_id: str = Field(..., description="Conversation ID for follow-up messages")
    timestamp: str = Field(..., description="Response timestamp")
    thinking: Optional[List[str]] = Field(None, description="Agent's thinking/reasoning process")
    is_json: bool = Field(False, description="Whether response is structured JSON")

    class Config:
        json_schema_extra = {
            "example": {
                "response": "Hello! How can I help you today?",
                "conversation_id": "b3348c39-a566-4bae-934c-6f4d78ad7b73",
                "timestamp": "2025-10-15T10:30:00Z",
                "thinking": ["[Thinking] Analyzing user greeting", "[Reasoning] Responding with friendly greeting"]
            }
        }


class ConversationResponse(BaseModel):
    """Response model for conversation operations"""
    conversation_id: str = Field(..., description="Unique conversation identifier")
    status: str = Field(..., description="Conversation status")
    created_at: str = Field(..., description="Creation timestamp")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    agent: str
    environment_id: str
    initialized: bool


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None


# Helper Functions
def get_client() -> CopilotAgentClient:
    """Get or create the Copilot client"""
    global copilot_client
    if copilot_client is None:
        copilot_client = CopilotAgentClient()
    return copilot_client


# API Endpoints

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Copilot Studio Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "POST /message": "Send a message to the agent",
            "POST /conversation/start": "Start a new conversation",
            "GET /conversation/{id}": "Get conversation details",
            "DELETE /conversation/{id}": "End a conversation",
            "GET /health": "Health check"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        client = get_client()
        config_info = client.get_config_info()

        return HealthResponse(
            status="healthy",
            agent=config_info["agent"]["schema_name"],
            environment_id=config_info["agent"]["environment_id"],
            initialized=config_info["initialized"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.post("/message", response_model=MessageResponse, tags=["Messaging"])
async def send_message(request: MessageRequest):
    """
    Send a message to the Copilot agent

    - **message**: The message to send to the agent
    - **conversation_id**: Optional conversation ID to maintain context

    Returns the agent's response with conversation ID for follow-up messages.
    """
    try:
        client = get_client()

        # Send message (SDK handles conversation internally if no ID provided)
        response_text = await client.send_message_async(
            message=request.message,
            conversation_id=request.conversation_id
        )

        # Extract conversation ID (for now, generate if not provided)
        conv_id = request.conversation_id
        if not conv_id:
            # Start a new conversation
            conv_result = await client.start_conversation_async()
            conv_id = conv_result["conversation_id"]

        # Check if response is already parsed JSON (dict)
        is_json_response = isinstance(response_text, dict)

        if is_json_response:
            # Response is already parsed JSON
            return MessageResponse(
                response=response_text,
                conversation_id=conv_id,
                timestamp=datetime.utcnow().isoformat() + "Z",
                thinking=None,  # Thinking extracted separately if needed
                is_json=True
            )
        else:
            # Response is text - check for thinking process
            thinking_lines = []
            response_lines = []
            for line in response_text.split("\n"):
                if line.startswith("[Thinking]") or line.startswith("[Reasoning]"):
                    thinking_lines.append(line)
                elif line.strip():
                    response_lines.append(line)

            return MessageResponse(
                response="\n".join(response_lines) if response_lines else response_text,
                conversation_id=conv_id,
                timestamp=datetime.utcnow().isoformat() + "Z",
                thinking=thinking_lines if thinking_lines else None,
                is_json=False
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/conversation/start", response_model=ConversationResponse, tags=["Conversations"])
async def start_conversation():
    """
    Start a new conversation with the agent

    Returns a conversation ID that can be used for subsequent messages.
    """
    try:
        client = get_client()
        result = await client.start_conversation_async()

        conversation_id = result["conversation_id"]

        # Store conversation metadata
        conversations[conversation_id] = {
            "started_at": datetime.utcnow().isoformat(),
            "message_count": 0
        }

        return ConversationResponse(
            conversation_id=conversation_id,
            status="active",
            created_at=datetime.utcnow().isoformat() + "Z"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversation/{conversation_id}", tags=["Conversations"])
async def get_conversation(conversation_id: str):
    """Get conversation details"""
    if conversation_id in conversations:
        return {
            "conversation_id": conversation_id,
            "status": "active",
            **conversations[conversation_id]
        }
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")


@app.delete("/conversation/{conversation_id}", tags=["Conversations"])
async def delete_conversation(conversation_id: str):
    """End/delete a conversation"""
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"status": "deleted", "conversation_id": conversation_id}
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")


@app.get("/conversations", tags=["Conversations"])
async def list_conversations():
    """List all active conversations"""
    return {
        "total": len(conversations),
        "conversations": [
            {"conversation_id": cid, **data}
            for cid, data in conversations.items()
        ]
    }


@app.get("/config", tags=["Configuration"])
async def get_config():
    """Get current agent configuration"""
    try:
        client = get_client()
        return client.get_config_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Startup and Shutdown Events
@app.on_event("startup")
async def startup_event():
    """Initialize the Copilot client on startup"""
    print("=" * 60)
    print("Copilot Studio Agent API Starting...")
    print("=" * 60)
    try:
        client = get_client()
        print("✓ Copilot client ready")
    except Exception as e:
        print(f"Warning: Could not pre-initialize client: {e}")
        print("Client will be initialized on first request")
    print("=" * 60)
    print("API is ready!")
    print("Visit http://localhost:8000/docs for interactive documentation")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("\nShutting down Copilot Studio Agent API...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
