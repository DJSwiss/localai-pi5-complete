#!/usr/bin/env python3
"""
MCP Gateway - Connects LocalAI agents to MCP servers
Provides unified interface for tool execution and resource access
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import openai
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MCP Gateway", version="1.0.0")

# Configuration
LOCALAI_BASE_URL = "http://localai-mcp:8080"
MCP_SERVER_URL = "http://mcp-server:8093"
MCP_RESOURCES_URL = "http://mcp-resources:8094"

# Configure OpenAI client for LocalAI
openai.api_base = f"{LOCALAI_BASE_URL}/v1"
openai.api_key = "not-needed-for-localai"

class MCPRequest(BaseModel):
    operation: str
    target: str
    parameters: Dict[str, Any] = {}

class MCPResponse(BaseModel):
    success: bool
    data: Any
    error: Optional[str] = None
    source: str

class AgentMCPRequest(BaseModel):
    message: str
    agent_type: str = "general"
    use_mcp: bool = True
    max_iterations: int = 10

class AgentMCPResponse(BaseModel):
    response: str
    mcp_calls: List[Dict] = []
    iterations: int = 0
    status: str = "completed"

# MCP Server Interface
class MCPClient:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP server tool"""
        try:
            response = await self.client.post(
                f"{MCP_SERVER_URL}/tools/{tool_name}",
                json=arguments
            )
            return response.json()
        except Exception as e:
            logger.error(f"MCP tool call failed: {e}")
            return {"error": str(e)}
    
    async def get_resource(self, resource_uri: str) -> Dict[str, Any]:
        """Get MCP resource"""
        try:
            response = await self.client.get(
                f"{MCP_RESOURCES_URL}/resources",
                params={"uri": resource_uri}
            )
            return response.json()
        except Exception as e:
            logger.error(f"MCP resource access failed: {e}")
            return {"error": str(e)}
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available MCP tools"""
        try:
            response = await self.client.get(f"{MCP_SERVER_URL}/tools")
            return response.json().get("tools", [])
        except Exception as e:
            logger.error(f"Failed to list MCP tools: {e}")
            return []
    
    async def list_resources(self) -> List[str]:
        """List available MCP resources"""
        try:
            response = await self.client.get(f"{MCP_RESOURCES_URL}/resources")
            return response.json().get("resources", [])
        except Exception as e:
            logger.error(f"Failed to list MCP resources: {e}")
            return []

# Global MCP client
mcp_client = MCPClient()

@app.get("/")
async def root():
    return {
        "message": "MCP Gateway for LocalAI",
        "status": "running",
        "services": {
            "localai": LOCALAI_BASE_URL,
            "mcp_server": MCP_SERVER_URL,
            "mcp_resources": MCP_RESOURCES_URL
        }
    }

@app.get("/health")
async def health_check():
    """Check health of all connected services"""
    health = {
        "gateway": "healthy",
        "timestamp": datetime.now().isoformat()
    }
    
    # Check LocalAI
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{LOCALAI_BASE_URL}/readyz", timeout=5.0)
            health["localai"] = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        health["localai"] = "unreachable"
    
    # Check MCP Server
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MCP_SERVER_URL}/", timeout=5.0)
            health["mcp_server"] = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        health["mcp_server"] = "unreachable"
    
    # Check MCP Resources
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MCP_RESOURCES_URL}/", timeout=5.0)
            health["mcp_resources"] = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        health["mcp_resources"] = "unreachable"
    
    return health

@app.get("/mcp/tools")
async def list_mcp_tools():
    """List all available MCP tools"""
    tools = await mcp_client.list_tools()
    return {"tools": tools}

@app.get("/mcp/resources")
async def list_mcp_resources():
    """List all available MCP resources"""
    resources = await mcp_client.list_resources()
    return {"resources": resources}

@app.post("/mcp/execute", response_model=MCPResponse)
async def execute_mcp_operation(request: MCPRequest):
    """Execute MCP operation (tool or resource access)"""
    
    try:
        if request.operation == "tool":
            result = await mcp_client.call_tool(request.target, request.parameters)
            return MCPResponse(
                success=True,
                data=result,
                source="mcp_server"
            )
        
        elif request.operation == "resource":
            result = await mcp_client.get_resource(request.target)
            return MCPResponse(
                success=True,
                data=result,
                source="mcp_resources"
            )
        
        else:
            return MCPResponse(
                success=False,
                error=f"Unknown operation: {request.operation}",
                data=None,
                source="gateway"
            )
    
    except Exception as e:
        return MCPResponse(
            success=False,
            error=str(e),
            data=None,
            source="gateway"
        )

@app.post("/agent/chat", response_model=AgentMCPResponse)
async def chat_with_mcp_agent(request: AgentMCPRequest):
    """Enhanced agent chat with MCP integration"""
    
    try:
        messages = [
            {
                "role": "system",
                "content": get_mcp_agent_prompt(request.agent_type)
            },
            {
                "role": "user",
                "content": request.message
            }
        ]
        
        mcp_calls = []
        iterations = 0
        
        # Get available MCP tools for context
        available_tools = await mcp_client.list_tools() if request.use_mcp else []
        
        for iteration in range(request.max_iterations):
            iterations = iteration + 1
            
            # Enhanced system message with MCP context
            if request.use_mcp and available_tools:
                mcp_context = f"\n\nAvailable MCP tools: {[tool['name'] for tool in available_tools[:5]]}"
                messages[0]["content"] += mcp_context
            
            # Call LocalAI
            response = openai.ChatCompletion.create(
                model="phi-2",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            assistant_message = response.choices[0].message.content
            
            # Check if agent wants to use MCP tools (simple pattern matching)
            if request.use_mcp and any(keyword in assistant_message.lower() for keyword in 
                                     ['system info', 'docker', 'file', 'network', 'model']):
                
                # Determine appropriate MCP call
                mcp_call = await suggest_mcp_call(assistant_message)
                
                if mcp_call:
                    logger.info(f"Making suggested MCP call: {mcp_call}")
                    mcp_result = await execute_mcp_call(mcp_call)
                    
                    mcp_calls.append({
                        "call": mcp_call,
                        "result": mcp_result,
                        "iteration": iteration + 1
                    })
                    
                    # Add MCP result to conversation
                    messages.append({
                        "role": "assistant",
                        "content": assistant_message
                    })
                    
                    messages.append({
                        "role": "user",
                        "content": f"MCP tool result: {json.dumps(mcp_result)}"
                    })
                    
                    # Continue conversation with MCP result
                    continue
            
            # No MCP call needed or made
            return AgentMCPResponse(
                response=assistant_message,
                mcp_calls=mcp_calls,
                iterations=iterations,
                status="completed"
            )
        
        return AgentMCPResponse(
            response="Maximum iterations reached",
            mcp_calls=mcp_calls,
            iterations=iterations,
            status="max_iterations_reached"
        )
        
    except Exception as e:
        logger.error(f"MCP Agent chat error: {e}")
        return AgentMCPResponse(
            response=f"Error: {str(e)}",
            mcp_calls=[],
            iterations=0,
            status="error"
        )

async def suggest_mcp_call(message: str) -> Optional[Dict[str, Any]]:
    """Suggest appropriate MCP call based on message content"""
    message_lower = message.lower()
    
    # System information requests
    if any(word in message_lower for word in ['system', 'memory', 'cpu', 'temperature']):
        return {
            "operation": "tool",
            "target": "get_system_info",
            "parameters": {"detailed": True}
        }
    
    # Docker management
    if any(word in message_lower for word in ['docker', 'container']):
        return {
            "operation": "tool", 
            "target": "manage_docker_containers",
            "parameters": {"action": "list"}
        }
    
    # File operations
    if any(word in message_lower for word in ['file', 'directory', 'folder']):
        return {
            "operation": "tool",
            "target": "file_manager", 
            "parameters": {"operation": "list", "path": "/mcp"}
        }
    
    # Network diagnostics
    if any(word in message_lower for word in ['network', 'ping', 'connection']):
        return {
            "operation": "tool",
            "target": "network_diagnostics",
            "parameters": {"test_type": "ping"}
        }
    
    # Dataset access
    if any(word in message_lower for word in ['dataset', 'data']):
        return {
            "operation": "resource",
            "target": "datasets://list",
            "parameters": {}
        }
    
    return None

async def execute_mcp_call(call: Dict[str, Any]) -> Dict[str, Any]:
    """Execute an MCP call"""
    try:
        if call["operation"] == "tool":
            return await mcp_client.call_tool(call["target"], call["parameters"])
        elif call["operation"] == "resource":
            return await mcp_client.get_resource(call["target"])
        else:
            return {"error": f"Unknown MCP operation: {call['operation']}"}
    except Exception as e:
        return {"error": str(e)}

def get_mcp_agent_prompt(agent_type: str) -> str:
    """Get enhanced system prompt with MCP capabilities"""
    
    base_prompt = """You are an AI assistant running on Raspberry Pi 5 with LocalAI and MCP (Model Context Protocol) integration. 
You have access to advanced system tools and resources through MCP servers."""
    
    if agent_type == "system":
        return f"""{base_prompt}
You specialize in system monitoring, Docker management, and Raspberry Pi optimization.
You can access real-time system information, manage containers, and provide technical insights."""
    
    elif agent_type == "data":
        return f"""{base_prompt}
You specialize in data analysis and dataset management.
You can access datasets, perform queries, and provide data insights."""
    
    elif agent_type == "developer":
        return f"""{base_prompt}
You specialize in software development and debugging.
You can manage files, analyze code, and assist with development tasks."""
    
    else:
        return f"""{base_prompt}
You are a general-purpose assistant with access to system tools, data resources, and development capabilities.
Use MCP tools when appropriate to provide accurate and helpful responses."""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8095)