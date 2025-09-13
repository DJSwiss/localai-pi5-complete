#!/usr/bin/env python3
"""
LocalAI Agent Orchestrator Server
Provides AI agents with function calling capabilities on Raspberry Pi 5
"""

import json
import logging
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import requests
from datetime import datetime
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LocalAI Agent Orchestrator", version="1.0.0")

# Configure OpenAI client for LocalAI
openai.api_base = os.getenv("LOCALAI_BASE_URL", "http://localhost:8080") + "/v1"
openai.api_key = "not-needed-for-localai"

class AgentRequest(BaseModel):
    message: str
    agent_type: str = "general"
    max_iterations: int = 10
    tools_enabled: bool = True

class AgentResponse(BaseModel):
    response: str
    tool_calls: List[Dict] = []
    iterations: int = 0
    status: str = "completed"

# Available Tools for Agents
AVAILABLE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and country, e.g. London, UK"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "web_search",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform mathematical calculations",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "file_operations",
            "description": "Read, write, or list files",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["read", "write", "list"],
                        "description": "The file operation to perform"
                    },
                    "path": {
                        "type": "string",
                        "description": "File path"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write (for write operation)"
                    }
                },
                "required": ["operation", "path"]
            }
        }
    }
]

def call_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Execute a tool function call"""
    tools_server_url = "http://tools-server:8091"
    
    try:
        response = requests.post(
            f"{tools_server_url}/execute_tool",
            json={"tool_name": tool_name, "arguments": arguments},
            timeout=30
        )
        if response.status_code == 200:
            return response.json().get("result", "Tool executed successfully")
        else:
            return f"Tool execution failed: {response.text}"
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return f"Error executing tool: {str(e)}"

@app.get("/")
async def root():
    return {
        "message": "LocalAI Agent Orchestrator",
        "status": "running",
        "available_agents": ["general", "researcher", "assistant", "coder"],
        "tools_available": len(AVAILABLE_TOOLS)
    }

@app.get("/agents")
async def list_agents():
    return {
        "agents": [
            {
                "name": "general",
                "description": "General purpose agent with tool access"
            },
            {
                "name": "researcher",
                "description": "Research-focused agent with web search capabilities"
            },
            {
                "name": "assistant",
                "description": "Personal assistant agent"
            },
            {
                "name": "coder",
                "description": "Programming and code analysis agent"
            }
        ]
    }

@app.get("/tools")
async def list_tools():
    return {"tools": AVAILABLE_TOOLS}

@app.post("/chat", response_model=AgentResponse)
async def chat_with_agent(request: AgentRequest):
    """Main agent chat endpoint with function calling"""
    
    try:
        messages = [
            {
                "role": "system",
                "content": get_agent_system_prompt(request.agent_type)
            },
            {
                "role": "user", 
                "content": request.message
            }
        ]
        
        tools = AVAILABLE_TOOLS if request.tools_enabled else []
        tool_calls_made = []
        iterations = 0
        
        for iteration in range(request.max_iterations):
            iterations = iteration + 1
            
            # Make request to LocalAI
            response = openai.ChatCompletion.create(
                model="phi-2",  # Use Pi 5-friendly model
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None,
                temperature=0.7,
                max_tokens=1000
            )
            
            message = response.choices[0].message
            
            # Check if the model wants to call a function
            if message.get("tool_calls"):
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"Calling tool: {function_name} with args: {arguments}")
                    
                    # Execute the tool
                    tool_result = call_tool(function_name, arguments)
                    
                    tool_calls_made.append({
                        "tool": function_name,
                        "arguments": arguments,
                        "result": tool_result
                    })
                    
                    # Add tool call and result to conversation
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": message.tool_calls
                    })
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result
                    })
            else:
                # No more tool calls, return the response
                return AgentResponse(
                    response=message.content,
                    tool_calls=tool_calls_made,
                    iterations=iterations,
                    status="completed"
                )
        
        return AgentResponse(
            response="Maximum iterations reached",
            tool_calls=tool_calls_made,
            iterations=iterations,
            status="max_iterations_reached"
        )
        
    except Exception as e:
        logger.error(f"Agent chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def get_agent_system_prompt(agent_type: str) -> str:
    """Get system prompt for different agent types"""
    
    prompts = {
        "general": """You are a helpful AI assistant running on a Raspberry Pi 5 with LocalAI. 
You have access to various tools to help users. Use the available tools when needed to provide accurate and helpful responses.
Always explain what you're doing when using tools.""",
        
        "researcher": """You are a research assistant with access to web search capabilities.
Your goal is to find accurate, up-to-date information on any topic. 
Always cite your sources and use web search when you need current information.""",
        
        "assistant": """You are a personal AI assistant running locally on Raspberry Pi 5.
You can help with tasks, calculations, file operations, and general questions.
You prioritize user privacy and all processing happens locally.""",
        
        "coder": """You are a programming assistant specializing in code analysis, debugging, and development.
You can help with various programming languages and have access to file operations for code review.
Focus on clean, efficient, and well-documented code."""
    }
    
    return prompts.get(agent_type, prompts["general"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8090)