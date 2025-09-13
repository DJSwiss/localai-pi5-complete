#!/usr/bin/env python3
"""
Tools Server for LocalAI Agents
Provides actual tool implementations for agent function calling
"""

import os
import json
import logging
import subprocess
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LocalAI Tools Server", version="1.0.0")

class ToolRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]

class ToolResponse(BaseModel):
    result: str
    success: bool = True
    error: str = None

@app.get("/")
async def root():
    return {
        "message": "LocalAI Tools Server",
        "status": "running",
        "available_tools": [
            "get_weather", "web_search", "calculate", 
            "file_operations", "system_info", "network_test"
        ]
    }

@app.post("/execute_tool", response_model=ToolResponse)
async def execute_tool(request: ToolRequest):
    """Execute a tool function"""
    
    try:
        tool_name = request.tool_name
        arguments = request.arguments
        
        logger.info(f"Executing tool: {tool_name} with args: {arguments}")
        
        # Route to appropriate tool function
        if tool_name == "get_weather":
            result = await get_weather(arguments.get("location"))
        elif tool_name == "web_search":
            result = await web_search(arguments.get("query"))
        elif tool_name == "calculate":
            result = await calculate(arguments.get("expression"))
        elif tool_name == "file_operations":
            result = await file_operations(
                arguments.get("operation"),
                arguments.get("path"),
                arguments.get("content")
            )
        elif tool_name == "system_info":
            result = await system_info()
        elif tool_name == "network_test":
            result = await network_test(arguments.get("host", "8.8.8.8"))
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        return ToolResponse(result=result, success=True)
        
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return ToolResponse(
            result="",
            success=False,
            error=str(e)
        )

async def get_weather(location: str) -> str:
    """Get weather information (mock implementation)"""
    # In a real implementation, you'd use a weather API
    # For demo purposes, returning mock data
    return f"Weather in {location}: Partly cloudy, 22°C (72°F), Humidity: 65%, Wind: 10 km/h"

async def web_search(query: str) -> str:
    """Perform web search (simplified implementation)"""
    try:
        # Using DuckDuckGo for privacy-friendly search
        from duckduckgo_search import DDGS
        
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            
        search_results = []
        for result in results:
            search_results.append(f"**{result['title']}**\n{result['body']}\nSource: {result['href']}\n")
        
        return "\n".join(search_results)
        
    except ImportError:
        # Fallback if duckduckgo-search is not available
        return f"Web search for '{query}': Mock results - DuckDuckGo search integration needed for real results."
    except Exception as e:
        return f"Search error: {str(e)}"

async def calculate(expression: str) -> str:
    """Safe mathematical calculation"""
    try:
        # Basic safety check
        allowed_chars = set("0123456789+-*/().,= ")
        if not all(c in allowed_chars for c in expression):
            return "Error: Expression contains invalid characters"
        
        # Evaluate safely
        result = eval(expression)
        return f"{expression} = {result}"
        
    except Exception as e:
        return f"Calculation error: {str(e)}"

async def file_operations(operation: str, path: str, content: str = None) -> str:
    """Safe file operations"""
    try:
        # Security: Only allow operations in specific directories
        allowed_dirs = ["/tools", "/agents", "/logs"]
        if not any(path.startswith(d) for d in allowed_dirs):
            return "Error: File operations only allowed in designated directories"
        
        if operation == "read":
            if os.path.exists(path):
                with open(path, 'r') as f:
                    content = f.read()
                return f"Content of {path}:\n{content}"
            else:
                return f"File {path} not found"
                
        elif operation == "write":
            if content is None:
                return "Error: Content required for write operation"
            with open(path, 'w') as f:
                f.write(content)
            return f"Successfully wrote to {path}"
            
        elif operation == "list":
            if os.path.isdir(path):
                files = os.listdir(path)
                return f"Files in {path}:\n" + "\n".join(files)
            else:
                return f"{path} is not a directory"
                
        else:
            return f"Unknown file operation: {operation}"
            
    except Exception as e:
        return f"File operation error: {str(e)}"

async def system_info() -> str:
    """Get Raspberry Pi system information"""
    try:
        info = []
        
        # CPU info
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpu_info = f.read()
                if 'Raspberry Pi' in cpu_info:
                    info.append("🍓 Raspberry Pi detected")
        except:
            pass
            
        # Memory info
        try:
            result = subprocess.run(['free', '-h'], capture_output=True, text=True)
            info.append(f"Memory usage:\n{result.stdout}")
        except:
            pass
            
        # Disk usage
        try:
            result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
            info.append(f"Disk usage:\n{result.stdout}")
        except:
            pass
            
        # Temperature (Pi-specific)
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = int(f.read()) / 1000
                info.append(f"CPU Temperature: {temp:.1f}°C")
        except:
            pass
        
        return "\n\n".join(info) if info else "System information unavailable"
        
    except Exception as e:
        return f"System info error: {str(e)}"

async def network_test(host: str = "8.8.8.8") -> str:
    """Test network connectivity"""
    try:
        result = subprocess.run(
            ['ping', '-c', '3', host], 
            capture_output=True, 
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return f"✅ Network connectivity to {host} is working\n{result.stdout}"
        else:
            return f"❌ Network connectivity to {host} failed\n{result.stderr}"
            
    except subprocess.TimeoutExpired:
        return f"❌ Network test to {host} timed out"
    except Exception as e:
        return f"Network test error: {str(e)}"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8091)