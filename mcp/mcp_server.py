#!/usr/bin/env python3
"""
MCP Server for LocalAI on Raspberry Pi 5
Provides tools, resources, and prompts via Model Context Protocol
"""

import asyncio
import json
import logging
import os
import psutil
import docker
from datetime import datetime
from typing import Dict, List, Any, Optional
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, EmbeddedResource
import requests
import subprocess

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("LocalAI-Pi5-MCP")

# Docker client for container management
try:
    docker_client = docker.from_env()
    docker_available = True
except:
    docker_available = False
    logger.warning("Docker not available for container management")

@mcp.tool()
async def get_system_info(detailed: bool = False) -> Dict[str, Any]:
    """Get comprehensive Raspberry Pi 5 system information"""
    info = {
        "timestamp": datetime.now().isoformat(),
        "hostname": os.uname().nodename,
        "platform": f"{os.uname().sysname} {os.uname().release}",
    }
    
    # CPU Information
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            if 'Raspberry Pi' in cpuinfo:
                info["device"] = "Raspberry Pi detected"
                # Extract Pi model info
                for line in cpuinfo.split('\n'):
                    if 'Model' in line:
                        info["model"] = line.split(':')[1].strip()
                        break
    except:
        pass
    
    # Memory info
    memory = psutil.virtual_memory()
    info["memory"] = {
        "total": f"{memory.total // (1024**3):.1f}GB",
        "available": f"{memory.available // (1024**3):.1f}GB",
        "used_percent": f"{memory.percent:.1f}%"
    }
    
    # CPU usage and temperature
    info["cpu"] = {
        "usage_percent": psutil.cpu_percent(interval=1),
        "core_count": psutil.cpu_count(),
        "frequency": f"{psutil.cpu_freq().current:.0f}MHz" if psutil.cpu_freq() else "Unknown"
    }
    
    # Pi-specific temperature
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = int(f.read()) / 1000
            info["temperature"] = f"{temp:.1f}°C"
    except:
        pass
    
    if detailed:
        # Disk usage
        disk = psutil.disk_usage('/')
        info["disk"] = {
            "total": f"{disk.total // (1024**3):.1f}GB",
            "free": f"{disk.free // (1024**3):.1f}GB",
            "used_percent": f"{(disk.used/disk.total)*100:.1f}%"
        }
        
        # Network info
        network = psutil.net_io_counters()
        info["network"] = {
            "bytes_sent": f"{network.bytes_sent // (1024**2):.1f}MB",
            "bytes_recv": f"{network.bytes_recv // (1024**2):.1f}MB"
        }
    
    return info

@mcp.tool()
async def manage_docker_containers(action: str, container_name: str = None) -> str:
    """Manage Docker containers (list, start, stop, restart, logs)"""
    if not docker_available:
        return "Docker is not available on this system"
    
    try:
        if action == "list":
            containers = docker_client.containers.list(all=True)
            result = []
            for container in containers:
                result.append({
                    "name": container.name,
                    "status": container.status,
                    "image": container.image.tags[0] if container.image.tags else "unknown",
                    "ports": [f"{p['HostPort']}:{p['PrivatePort']}" for p in container.ports] if container.ports else []
                })
            return json.dumps(result, indent=2)
        
        elif action in ["start", "stop", "restart"] and container_name:
            container = docker_client.containers.get(container_name)
            
            if action == "start":
                container.start()
                return f"Started container: {container_name}"
            elif action == "stop":
                container.stop()
                return f"Stopped container: {container_name}"
            elif action == "restart":
                container.restart()
                return f"Restarted container: {container_name}"
        
        elif action == "logs" and container_name:
            container = docker_client.containers.get(container_name)
            logs = container.logs(tail=50).decode('utf-8')
            return f"Logs for {container_name}:\n{logs}"
        
        else:
            return f"Invalid action or missing container name. Actions: list, start, stop, restart, logs"
    
    except docker.errors.NotFound:
        return f"Container {container_name} not found"
    except Exception as e:
        return f"Docker operation failed: {str(e)}"

@mcp.tool()
async def file_manager(operation: str, path: str, content: str = None, recursive: bool = False) -> str:
    """Advanced file management with safety restrictions"""
    # Security: Define allowed directories
    allowed_dirs = ["/mcp", "/agents", "/tools", "/training", "/models", "/logs"]
    
    if not any(path.startswith(d) for d in allowed_dirs):
        return f"File operations restricted to: {', '.join(allowed_dirs)}"
    
    try:
        if operation == "read":
            if os.path.isfile(path):
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                return f"Content of {path}:\n{content}"
            else:
                return f"File {path} not found"
        
        elif operation == "write":
            if content is None:
                return "Content required for write operation"
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote to {path}"
        
        elif operation == "list":
            if os.path.isdir(path):
                items = []
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path):
                        items.append(f"📁 {item}/")
                    else:
                        size = os.path.getsize(item_path)
                        items.append(f"📄 {item} ({size} bytes)")
                return f"Contents of {path}:\n" + "\n".join(items)
            else:
                return f"{path} is not a directory"
        
        elif operation == "delete":
            if os.path.exists(path):
                if os.path.isfile(path):
                    os.remove(path)
                    return f"Deleted file: {path}"
                elif os.path.isdir(path):
                    if recursive:
                        import shutil
                        shutil.rmtree(path)
                        return f"Deleted directory and contents: {path}"
                    else:
                        os.rmdir(path)
                        return f"Deleted empty directory: {path}"
            else:
                return f"Path {path} not found"
        
        else:
            return f"Unknown operation: {operation}. Available: read, write, list, delete"
    
    except Exception as e:
        return f"File operation failed: {str(e)}"

@mcp.tool()
async def network_diagnostics(target: str = "8.8.8.8", test_type: str = "ping") -> str:
    """Network connectivity and performance diagnostics"""
    try:
        if test_type == "ping":
            result = subprocess.run(
                ['ping', '-c', '4', target],
                capture_output=True,
                text=True,
                timeout=20
            )
            
            if result.returncode == 0:
                return f"✅ Ping to {target} successful:\n{result.stdout}"
            else:
                return f"❌ Ping to {target} failed:\n{result.stderr}"
        
        elif test_type == "traceroute":
            result = subprocess.run(
                ['traceroute', '-m', '15', target],
                capture_output=True,
                text=True,
                timeout=60
            )
            return f"Traceroute to {target}:\n{result.stdout}"
        
        elif test_type == "port":
            # Simple port check using netcat
            port = 80  # default HTTP port
            if ':' in target:
                target, port = target.split(':')
                port = int(port)
            
            result = subprocess.run(
                ['nc', '-z', '-v', target, str(port)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return f"✅ Port {port} on {target} is open"
            else:
                return f"❌ Port {port} on {target} is closed or filtered"
        
        else:
            return f"Unknown test type: {test_type}. Available: ping, traceroute, port"
    
    except subprocess.TimeoutExpired:
        return f"❌ Network test to {target} timed out"
    except Exception as e:
        return f"Network diagnostic failed: {str(e)}"

@mcp.tool()
async def ai_model_manager(action: str, model_name: str = None, model_path: str = None) -> str:
    """Manage AI models for LocalAI"""
    models_dir = "/models"
    
    try:
        if action == "list":
            if os.path.exists(models_dir):
                models = []
                for item in os.listdir(models_dir):
                    item_path = os.path.join(models_dir, item)
                    if os.path.isfile(item_path):
                        size = os.path.getsize(item_path) // (1024**2)  # MB
                        models.append(f"{item} ({size}MB)")
                return f"Available models:\n" + "\n".join(models)
            else:
                return "Models directory not found"
        
        elif action == "info" and model_name:
            model_path = os.path.join(models_dir, model_name)
            if os.path.exists(model_path):
                stat = os.stat(model_path)
                return f"Model: {model_name}\nSize: {stat.st_size // (1024**2)}MB\nModified: {datetime.fromtimestamp(stat.st_mtime)}"
            else:
                return f"Model {model_name} not found"
        
        elif action == "download" and model_name:
            # This would integrate with model downloading logic
            return f"Model download functionality would be implemented here for {model_name}"
        
        else:
            return f"Invalid action. Available: list, info, download"
    
    except Exception as e:
        return f"Model management failed: {str(e)}"

# Resources for data access
@mcp.resource("system://info")
async def system_resource() -> str:
    """System information resource"""
    info = await get_system_info(detailed=True)
    return json.dumps(info, indent=2)

@mcp.resource("logs://{service}")
async def logs_resource(service: str) -> str:
    """Access service logs"""
    log_paths = {
        "mcp": "/logs/mcp.log",
        "agent": "/logs/agent.log", 
        "training": "/logs/training.log"
    }
    
    log_path = log_paths.get(service, f"/logs/{service}.log")
    
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            return f.read()
    else:
        return f"Log file {log_path} not found"

@mcp.resource("models://{model_name}")
async def model_resource(model_name: str) -> str:
    """Access model information"""
    model_path = f"/models/{model_name}"
    
    if os.path.exists(model_path):
        stat = os.stat(model_path)
        info = {
            "name": model_name,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "path": model_path
        }
        return json.dumps(info, indent=2)
    else:
        return f"Model {model_name} not found"

# Prompts for different tasks
@mcp.prompt()
async def system_analysis_prompt(focus: str = "general", include_metrics: bool = True) -> str:
    """Generate prompts for system analysis tasks"""
    base = "You are analyzing a Raspberry Pi 5 system running LocalAI with MCP integration."
    
    if focus == "performance":
        return f"{base} Focus on performance metrics, resource usage, and optimization opportunities."
    elif focus == "security":
        return f"{base} Focus on security aspects, access controls, and potential vulnerabilities."
    elif focus == "troubleshooting":
        return f"{base} Focus on identifying and resolving system issues."
    else:
        return f"{base} Provide a comprehensive system analysis covering all aspects."

@mcp.prompt()
async def docker_management_prompt(task: str = "overview") -> str:
    """Generate prompts for Docker container management"""
    base = "You are managing Docker containers for a LocalAI setup on Raspberry Pi 5."
    
    if task == "optimization":
        return f"{base} Focus on optimizing container performance and resource usage."
    elif task == "troubleshooting":
        return f"{base} Focus on diagnosing and fixing container issues."
    elif task == "security":
        return f"{base} Focus on container security and best practices."
    else:
        return f"{base} Provide comprehensive Docker management guidance."

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mcp_server:mcp", host="0.0.0.0", port=8093, reload=True)