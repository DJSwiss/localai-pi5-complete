#!/usr/bin/env python3
"""
Enhanced MCP Server with LocalRecall RAG Integration
Combines system tools with advanced memory and semantic search
"""

import asyncio
import json
import logging
import os
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from mcp.server.fastmcp import FastMCP
import httpx

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("LocalAI-MCP-Recall")

# Configuration
LOCALAI_URL = os.getenv("LOCALAI_BASE_URL", "http://localhost:8080")
LOCALRECALL_URL = os.getenv("LOCALRECALL_BASE_URL", "http://localhost:8088")

class RecallClient:
    """Client for LocalRecall RAG operations"""
    
    def __init__(self):
        self.base_url = LOCALRECALL_URL
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def add_document(self, content: str, metadata: Dict = None) -> Dict:
        """Add document to knowledge base"""
        try:
            payload = {
                "content": content,
                "metadata": metadata or {}
            }
            response = await self.client.post(f"{self.base_url}/api/add", json=payload)
            return response.json()
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            return {"error": str(e)}
    
    async def search(self, query: str, limit: int = 5) -> Dict:
        """Semantic search in knowledge base"""
        try:
            params = {"query": query, "limit": limit}
            response = await self.client.get(f"{self.base_url}/api/search", params=params)
            return response.json()
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {"error": str(e)}
    
    async def get_collections(self) -> Dict:
        """Get all collections"""
        try:
            response = await self.client.get(f"{self.base_url}/api/collections")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get collections: {e}")
            return {"error": str(e)}
    
    async def upload_file(self, file_path: str, collection: str = "default") -> Dict:
        """Upload file to LocalRecall"""
        try:
            with open(file_path, 'rb') as f:
                files = {"file": f}
                data = {"collection": collection}
                response = requests.post(f"{self.base_url}/api/upload", files=files, data=data)
                return response.json()
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            return {"error": str(e)}

# Global recall client
recall = RecallClient()

@mcp.tool()
async def memory_store(content: str, category: str = "general", tags: List[str] = None) -> str:
    """Store information in long-term memory with LocalRecall"""
    metadata = {
        "category": category,
        "tags": tags or [],
        "timestamp": datetime.now().isoformat(),
        "source": "user_interaction"
    }
    
    result = await recall.add_document(content, metadata)
    
    if "error" in result:
        return f"❌ Failed to store memory: {result['error']}"
    
    return f"✅ Memory stored successfully! ID: {result.get('id', 'unknown')}"

@mcp.tool()
async def memory_recall(query: str, limit: int = 3) -> str:
    """Search through stored memories and knowledge"""
    result = await recall.search(query, limit)
    
    if "error" in result:
        return f"❌ Memory search failed: {result['error']}"
    
    if not result.get("results"):
        return "🤔 No relevant memories found for your query."
    
    memories = []
    for i, item in enumerate(result["results"][:limit], 1):
        content = item.get("content", "")[:200] + "..." if len(item.get("content", "")) > 200 else item.get("content", "")
        score = item.get("score", 0)
        metadata = item.get("metadata", {})
        
        memories.append(f"**Memory {i}** (relevance: {score:.2f})\n{content}\n*Tags: {metadata.get('tags', [])}*")
    
    return "🧠 **Recalled Memories:**\n\n" + "\n\n".join(memories)

@mcp.tool()
async def knowledge_upload(file_path: str, collection: str = "documents") -> str:
    """Upload document to knowledge base"""
    if not os.path.exists(file_path):
        return f"❌ File not found: {file_path}"
    
    # Security check
    allowed_dirs = ["/recall-assets", "/training", "/logs", "/mcp"]
    if not any(file_path.startswith(d) for d in allowed_dirs):
        return f"❌ File access restricted to: {', '.join(allowed_dirs)}"
    
    result = await recall.upload_file(file_path, collection)
    
    if "error" in result:
        return f"❌ Upload failed: {result['error']}"
    
    return f"✅ Document uploaded to '{collection}' collection. Processed {result.get('chunks', 0)} chunks."

@mcp.tool()
async def conversation_context(action: str = "get", context_data: str = None) -> str:
    """Manage conversation context and history"""
    
    if action == "store" and context_data:
        # Store conversation turn
        metadata = {
            "category": "conversation",
            "timestamp": datetime.now().isoformat(),
            "type": "dialogue_turn"
        }
        
        result = await recall.add_document(context_data, metadata)
        return f"✅ Conversation context stored" if "error" not in result else f"❌ Failed to store context"
    
    elif action == "get":
        # Retrieve recent conversation context
        result = await recall.search("conversation dialogue", limit=5)
        
        if "error" in result or not result.get("results"):
            return "💬 Starting fresh conversation - no previous context found."
        
        context = []
        for item in result["results"]:
            content = item.get("content", "")[:150] + "..." if len(item.get("content", "")) > 150 else item.get("content", "")
            context.append(content)
        
        return "💬 **Recent Conversation Context:**\n\n" + "\n\n".join(context)
    
    else:
        return "❌ Invalid action. Use 'store' with context_data or 'get'"

@mcp.tool()
async def smart_qa(question: str, search_knowledge: bool = True) -> str:
    """Answer questions using RAG with LocalRecall + LocalAI"""
    
    context = ""
    
    if search_knowledge:
        # Search knowledge base for relevant information
        search_result = await recall.search(question, limit=3)
        
        if search_result.get("results"):
            contexts = []
            for result in search_result["results"]:
                contexts.append(result.get("content", ""))
            context = "\n\n".join(contexts)
    
    # Create enhanced prompt with context
    if context:
        prompt = f"""Based on the following context information, please answer the question.
        
Context:
{context}

Question: {question}

Please provide a comprehensive answer based on the context. If the context doesn't contain enough information, say so and provide what you can based on your general knowledge."""
    else:
        prompt = f"Question: {question}\n\nPlease provide a helpful answer."
    
    try:
        # Call LocalAI for generation
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LOCALAI_URL}/v1/chat/completions",
                json={
                    "model": "phi-2",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 500
                }
            )
            
            if response.status_code == 200:
                ai_response = response.json()["choices"][0]["message"]["content"]
                
                # Store this Q&A for future reference
                qa_content = f"Question: {question}\nAnswer: {ai_response}"
                await recall.add_document(qa_content, {
                    "category": "qa_session",
                    "timestamp": datetime.now().isoformat()
                })
                
                return f"🤖 **AI Answer:**\n\n{ai_response}"
            else:
                return f"❌ LocalAI request failed: {response.status_code}"
    
    except Exception as e:
        return f"❌ Error generating answer: {str(e)}"

@mcp.tool()
async def knowledge_summary(collection: str = "default", max_items: int = 10) -> str:
    """Summarize knowledge base contents"""
    try:
        # Get recent additions
        collections = await recall.get_collections()
        
        if "error" in collections:
            return f"❌ Failed to get collections: {collections['error']}"
        
        summary = f"📚 **Knowledge Base Summary**\n\n"
        
        if collections.get("collections"):
            summary += f"**Collections:** {len(collections['collections'])}\n"
            for coll in collections["collections"]:
                summary += f"  • {coll}\n"
        
        # Get a sample of recent documents
        sample_search = await recall.search("*", limit=max_items)
        
        if sample_search.get("results"):
            summary += f"\n**Recent Documents:** {len(sample_search['results'])}\n"
            
            categories = {}
            for doc in sample_search["results"]:
                metadata = doc.get("metadata", {})
                category = metadata.get("category", "uncategorized")
                categories[category] = categories.get(category, 0) + 1
            
            summary += "\n**Categories:**\n"
            for cat, count in categories.items():
                summary += f"  • {cat}: {count} items\n"
        
        return summary
    
    except Exception as e:
        return f"❌ Summary failed: {str(e)}"

# Resources with RAG integration
@mcp.resource("memory://search/{query}")
async def memory_search_resource(query: str) -> str:
    """Search memory as a resource"""
    result = await recall.search(query, limit=5)
    return json.dumps(result, indent=2)

@mcp.resource("knowledge://collections")
async def collections_resource() -> str:
    """Get all collections"""
    result = await recall.get_collections()
    return json.dumps(result, indent=2)

@mcp.resource("context://conversation")
async def conversation_resource() -> str:
    """Get conversation context"""
    result = await recall.search("conversation", limit=10)
    return json.dumps(result, indent=2)

# Enhanced prompts with memory context
@mcp.prompt()
async def rag_prompt(topic: str, style: str = "comprehensive") -> str:
    """Generate context-aware prompts using RAG"""
    
    # Search for relevant context
    context_result = await recall.search(topic, limit=3)
    
    context = ""
    if context_result.get("results"):
        context_items = [r.get("content", "") for r in context_result["results"]]
        context = "\n\n".join(context_items)
    
    if style == "comprehensive":
        return f"""You are an AI assistant with access to a knowledge base. Use the following context to provide a comprehensive response about {topic}.

Context from knowledge base:
{context}

Please provide a detailed, accurate response that incorporates both the context information and your general knowledge."""
    
    elif style == "concise":
        return f"""Based on the context below, provide a concise response about {topic}.

Context: {context}

Keep your response brief but informative."""
    
    else:
        return f"""Discuss {topic} using any relevant information from the following context:

{context}"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mcp_server_recall:mcp", host="0.0.0.0", port=8093, reload=True)