#!/usr/bin/env python3
"""
MCP Resources Server - Data Sources and Context Provider
Provides structured access to datasets, models, and knowledge bases
"""

import asyncio
import json
import logging
import os
import sqlite3
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, EmbeddedResource
import aiofiles
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server for resources
mcp = FastMCP("LocalAI-Resources")

class DatasetWatcher(FileSystemEventHandler):
    """Monitor dataset changes for real-time updates"""
    
    def __init__(self, callback):
        self.callback = callback
    
    def on_modified(self, event):
        if not event.is_directory:
            logger.info(f"Dataset modified: {event.src_path}")
            self.callback(event.src_path)

# Global dataset cache
dataset_cache = {}
file_observer = None

def setup_file_monitoring():
    """Setup file system monitoring for datasets"""
    global file_observer
    
    def on_dataset_change(path):
        # Invalidate cache for changed file
        if path in dataset_cache:
            del dataset_cache[path]
        logger.info(f"Cache invalidated for {path}")
    
    event_handler = DatasetWatcher(on_dataset_change)
    file_observer = Observer()
    
    # Monitor datasets directory
    datasets_path = os.getenv("DATA_PATH", "/datasets")
    if os.path.exists(datasets_path):
        file_observer.schedule(event_handler, datasets_path, recursive=True)
        file_observer.start()
        logger.info(f"Monitoring dataset changes in {datasets_path}")

@mcp.resource("datasets://list")
async def list_datasets() -> str:
    """List all available datasets"""
    datasets_path = os.getenv("DATA_PATH", "/datasets")
    
    if not os.path.exists(datasets_path):
        return json.dumps({"error": "Datasets directory not found"})
    
    datasets = []
    for root, dirs, files in os.walk(datasets_path):
        for file in files:
            if file.endswith(('.csv', '.json', '.jsonl', '.txt', '.tsv')):
                filepath = os.path.join(root, file)
                relative_path = os.path.relpath(filepath, datasets_path)
                
                stat = os.stat(filepath)
                datasets.append({
                    "name": relative_path,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "type": file.split('.')[-1]
                })
    
    return json.dumps({"datasets": datasets}, indent=2)

@mcp.resource("datasets://{dataset_name}")
async def get_dataset(dataset_name: str) -> str:
    """Get dataset content with caching"""
    datasets_path = os.getenv("DATA_PATH", "/datasets")
    full_path = os.path.join(datasets_path, dataset_name)
    
    if not os.path.exists(full_path):
        return json.dumps({"error": f"Dataset {dataset_name} not found"})
    
    # Check cache first
    if full_path in dataset_cache:
        logger.info(f"Using cached data for {dataset_name}")
        return dataset_cache[full_path]
    
    try:
        # Load based on file type
        if dataset_name.endswith('.csv'):
            df = pd.read_csv(full_path)
            data = {
                "name": dataset_name,
                "type": "csv",
                "shape": df.shape,
                "columns": df.columns.tolist(),
                "sample": df.head(5).to_dict('records'),
                "info": {
                    "memory_usage": df.memory_usage(deep=True).sum(),
                    "dtypes": df.dtypes.to_dict()
                }
            }
        
        elif dataset_name.endswith('.json'):
            async with aiofiles.open(full_path, 'r') as f:
                content = await f.read()
                json_data = json.loads(content)
                data = {
                    "name": dataset_name,
                    "type": "json",
                    "content": json_data if len(str(json_data)) < 10000 else "Large JSON - use specific queries",
                    "size": len(content)
                }
        
        elif dataset_name.endswith('.jsonl'):
            lines = []
            async with aiofiles.open(full_path, 'r') as f:
                count = 0
                async for line in f:
                    if count < 5:  # Sample first 5 lines
                        lines.append(json.loads(line.strip()))
                    count += 1
                
                data = {
                    "name": dataset_name,
                    "type": "jsonl",
                    "total_lines": count,
                    "sample": lines
                }
        
        elif dataset_name.endswith('.txt'):
            async with aiofiles.open(full_path, 'r') as f:
                content = await f.read()
                data = {
                    "name": dataset_name,
                    "type": "text",
                    "size": len(content),
                    "preview": content[:1000] + "..." if len(content) > 1000 else content,
                    "lines": content.count('\n') + 1
                }
        
        else:
            data = {"error": f"Unsupported file type for {dataset_name}"}
        
        # Cache the result
        result = json.dumps(data, indent=2, default=str)
        dataset_cache[full_path] = result
        
        return result
    
    except Exception as e:
        return json.dumps({"error": f"Failed to load {dataset_name}: {str(e)}"})

@mcp.resource("datasets://{dataset_name}/query")
async def query_dataset(dataset_name: str, query: str = None) -> str:
    """Query dataset with pandas operations"""
    datasets_path = os.getenv("DATA_PATH", "/datasets")
    full_path = os.path.join(datasets_path, dataset_name)
    
    if not os.path.exists(full_path):
        return json.dumps({"error": f"Dataset {dataset_name} not found"})
    
    try:
        if dataset_name.endswith('.csv'):
            df = pd.read_csv(full_path)
            
            # Basic queries
            if query == "describe":
                stats = df.describe(include='all').to_dict()
                return json.dumps({"statistics": stats}, default=str)
            
            elif query == "columns":
                return json.dumps({"columns": df.columns.tolist()})
            
            elif query == "sample":
                return json.dumps({"sample": df.sample(min(10, len(df))).to_dict('records')}, default=str)
            
            elif query == "info":
                info = {
                    "shape": df.shape,
                    "dtypes": df.dtypes.to_dict(),
                    "null_counts": df.isnull().sum().to_dict(),
                    "memory_usage": df.memory_usage(deep=True).sum()
                }
                return json.dumps({"info": info}, default=str)
            
            else:
                return json.dumps({"error": "Supported queries: describe, columns, sample, info"})
        
        else:
            return json.dumps({"error": "Querying only supported for CSV files"})
    
    except Exception as e:
        return json.dumps({"error": f"Query failed: {str(e)}"})

@mcp.resource("models://metadata")
async def models_metadata() -> str:
    """Get metadata for all available models"""
    models_path = os.getenv("MODELS_PATH", "/models")
    
    if not os.path.exists(models_path):
        return json.dumps({"error": "Models directory not found"})
    
    models = []
    for file in os.listdir(models_path):
        if file.endswith(('.gguf', '.bin', '.safetensors', '.pt', '.pth')):
            filepath = os.path.join(models_path, file)
            stat = os.stat(filepath)
            
            models.append({
                "name": file,
                "size_mb": stat.st_size // (1024 * 1024),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "type": file.split('.')[-1],
                "path": filepath
            })
    
    return json.dumps({"models": models}, indent=2)

@mcp.resource("knowledge://pi5")
async def raspberry_pi_knowledge() -> str:
    """Raspberry Pi 5 specific knowledge base"""
    knowledge = {
        "specs": {
            "cpu": "Broadcom BCM2712 quad-core Arm Cortex-A76 @ 2.4GHz",
            "memory": "4GB or 8GB LPDDR4X-4267",
            "gpu": "VideoCore VII GPU, supporting OpenGL ES 3.1, Vulkan 1.2",
            "connectivity": "2.4GHz and 5.0GHz IEEE 802.11ac wireless, Bluetooth 5.0, BLE",
            "ports": "2 × USB 3.0, 2 × USB 2.0, Gigabit Ethernet, 2 × 4-lane MIPI camera/display"
        },
        "optimization_tips": [
            "Use MMAP=true for model loading to reduce memory usage",
            "Set THREADS=4 to match the quad-core CPU",
            "Monitor temperature - throttling occurs above 80°C", 
            "Use f16=true for models to reduce memory usage",
            "Consider smaller models (≤3B parameters) for better performance"
        ],
        "troubleshooting": {
            "memory_issues": "Use swap file if needed, monitor with 'free -h'",
            "thermal_issues": "Check /sys/class/thermal/thermal_zone0/temp",
            "performance": "Check CPU governor: cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"
        }
    }
    
    return json.dumps(knowledge, indent=2)

@mcp.resource("logs://system")
async def system_logs() -> str:
    """Get recent system logs"""
    try:
        import subprocess
        result = subprocess.run(
            ['journalctl', '-n', '50', '--no-pager'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            return "Failed to retrieve system logs"
    
    except Exception as e:
        return f"Error accessing system logs: {str(e)}"

@mcp.resource("context://conversation")
async def conversation_context() -> str:
    """Maintain conversation context and memory"""
    # This would integrate with a proper context management system
    context = {
        "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "active_models": [],
        "recent_queries": [],
        "user_preferences": {},
        "system_state": "ready"
    }
    
    return json.dumps(context, indent=2)

# Tools for data manipulation
@mcp.tool()
async def create_dataset(name: str, data: str, format: str = "json") -> str:
    """Create a new dataset from provided data"""
    datasets_path = os.getenv("DATA_PATH", "/datasets")
    
    if not os.path.exists(datasets_path):
        os.makedirs(datasets_path)
    
    filepath = os.path.join(datasets_path, f"{name}.{format}")
    
    try:
        if format == "json":
            # Validate JSON
            json.loads(data)
            async with aiofiles.open(filepath, 'w') as f:
                await f.write(data)
        
        elif format == "csv":
            # Basic CSV validation
            async with aiofiles.open(filepath, 'w') as f:
                await f.write(data)
        
        else:
            return f"Unsupported format: {format}"
        
        return f"Dataset {name}.{format} created successfully"
    
    except Exception as e:
        return f"Failed to create dataset: {str(e)}"

@mcp.tool()
async def search_datasets(query: str, file_type: str = "all") -> str:
    """Search through dataset contents"""
    datasets_path = os.getenv("DATA_PATH", "/datasets")
    
    if not os.path.exists(datasets_path):
        return json.dumps({"error": "Datasets directory not found"})
    
    results = []
    
    for root, dirs, files in os.walk(datasets_path):
        for file in files:
            if file_type != "all" and not file.endswith(f".{file_type}"):
                continue
            
            filepath = os.path.join(root, file)
            try:
                # Simple text search for now
                if file.endswith('.txt'):
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if query.lower() in content.lower():
                            results.append({
                                "file": file,
                                "matches": content.lower().count(query.lower())
                            })
                
                elif file.endswith('.csv'):
                    df = pd.read_csv(filepath)
                    # Search in string columns
                    string_cols = df.select_dtypes(include=['object']).columns
                    for col in string_cols:
                        if df[col].astype(str).str.contains(query, case=False, na=False).any():
                            results.append({
                                "file": file,
                                "column": col,
                                "type": "csv"
                            })
                            break
            
            except Exception as e:
                logger.warning(f"Failed to search in {file}: {e}")
    
    return json.dumps({"results": results}, indent=2)

if __name__ == "__main__":
    # Setup file monitoring
    setup_file_monitoring()
    
    try:
        import uvicorn
        uvicorn.run("mcp_resources:mcp", host="0.0.0.0", port=8094, reload=True)
    finally:
        if file_observer:
            file_observer.stop()
            file_observer.join()