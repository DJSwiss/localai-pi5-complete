#!/usr/bin/env python3
"""
Streamlit Web UI for LocalAI Agents
Provides an easy-to-use interface for interacting with AI agents
"""

import streamlit as st
import requests
import json
from datetime import datetime
import os

# Configure Streamlit page
st.set_page_config(
    page_title="LocalAI Agents - Pi 5",
    page_icon="🤖",
    layout="wide"
)

# API URLs
LOCALAI_URL = os.getenv("LOCALAI_BASE_URL", "http://localhost:8080")
AGENT_URL = os.getenv("AGENT_ORCHESTRATOR_URL", "http://localhost:8090")

def main():
    st.title("🍓 LocalAI Agents on Raspberry Pi 5")
    st.markdown("---")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Agent selection
        agent_type = st.selectbox(
            "Choose Agent Type:",
            ["general", "researcher", "assistant", "coder"],
            help="Different agents have specialized capabilities"
        )
        
        # Tools toggle
        tools_enabled = st.checkbox("Enable Tools", value=True)
        
        # Max iterations
        max_iterations = st.slider("Max Tool Iterations", 1, 20, 10)
        
        st.markdown("---")
        st.header("📊 System Status")
        
        # Check system status
        if st.button("Check Status"):
            check_system_status()
    
    # Main chat interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Chat with Agent")
        
        # Chat input
        user_message = st.text_area(
            "Enter your message:",
            height=100,
            placeholder="Ask your AI agent anything! Try: 'What's the weather like?' or 'Calculate 15 * 23'"
        )
        
        # Send button
        if st.button("🚀 Send Message", type="primary"):
            if user_message.strip():
                with st.spinner("🤖 Agent is thinking..."):
                    response = send_message_to_agent(
                        user_message, 
                        agent_type, 
                        tools_enabled, 
                        max_iterations
                    )
                    display_agent_response(response)
            else:
                st.error("Please enter a message!")
        
        # Example prompts
        st.markdown("### 💡 Example Prompts")
        example_prompts = [
            "What's the current system information?",
            "Calculate the square root of 144",
            "Search for information about Raspberry Pi 5",
            "Create a simple Python function to add two numbers",
            "Test network connectivity to google.com"
        ]
        
        for prompt in example_prompts:
            if st.button(prompt, key=f"example_{prompt[:20]}"):
                with st.spinner("🤖 Agent is thinking..."):
                    response = send_message_to_agent(
                        prompt, 
                        agent_type, 
                        tools_enabled, 
                        max_iterations
                    )
                    display_agent_response(response)
    
    with col2:
        st.header("🔧 Available Tools")
        
        # Display available tools
        tools_info = get_available_tools()
        if tools_info:
            for tool in tools_info:
                with st.expander(f"🛠️ {tool['function']['name']}"):
                    st.write(f"**Description:** {tool['function']['description']}")
                    if 'parameters' in tool['function']:
                        st.write("**Parameters:**")
                        for param, details in tool['function']['parameters']['properties'].items():
                            st.write(f"- `{param}`: {details.get('description', 'No description')}")
        
        st.markdown("---")
        st.header("📈 Agent Types")
        
        agent_descriptions = {
            "general": "🤖 General purpose agent with access to all tools",
            "researcher": "🔍 Specialized in web search and information gathering",
            "assistant": "👤 Personal assistant for daily tasks and calculations",
            "coder": "💻 Programming focused agent for code-related tasks"
        }
        
        for agent, desc in agent_descriptions.items():
            if agent == agent_type:
                st.success(f"**{agent.title()}** (Selected)\n{desc}")
            else:
                st.info(f"**{agent.title()}**\n{desc}")

def send_message_to_agent(message, agent_type, tools_enabled, max_iterations):
    """Send message to the agent orchestrator"""
    try:
        payload = {
            "message": message,
            "agent_type": agent_type,
            "tools_enabled": tools_enabled,
            "max_iterations": max_iterations
        }
        
        response = requests.post(
            f"{AGENT_URL}/chat",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "response": f"Error: {response.status_code} - {response.text}",
                "tool_calls": [],
                "status": "error"
            }
    except requests.exceptions.ConnectionError:
        return {
            "response": "❌ Cannot connect to agent server. Make sure the agent services are running.",
            "tool_calls": [],
            "status": "connection_error"
        }
    except Exception as e:
        return {
            "response": f"Error: {str(e)}",
            "tool_calls": [],
            "status": "error"
        }

def display_agent_response(response):
    """Display the agent's response"""
    if response.get("status") == "error" or response.get("status") == "connection_error":
        st.error(response["response"])
        return
    
    # Display main response
    st.success(f"**Agent Response:**\n{response['response']}")
    
    # Display tool calls if any
    if response.get("tool_calls"):
        st.markdown("### 🔧 Tool Calls Made")
        for i, tool_call in enumerate(response["tool_calls"], 1):
            with st.expander(f"Tool Call {i}: {tool_call['tool']}"):
                st.write(f"**Arguments:** {tool_call['arguments']}")
                st.write(f"**Result:** {tool_call['result']}")
    
    # Display metadata
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Iterations Used", response.get("iterations", 0))
    with col2:
        st.metric("Status", response.get("status", "unknown"))

def get_available_tools():
    """Get list of available tools"""
    try:
        response = requests.get(f"{AGENT_URL}/tools", timeout=5)
        if response.status_code == 200:
            return response.json().get("tools", [])
    except:
        pass
    return []

def check_system_status():
    """Check the status of all services"""
    services = [
        ("LocalAI API", f"{LOCALAI_URL}/v1/models"),
        ("Agent Orchestrator", f"{AGENT_URL}/agents"),
        ("Tools Server", "http://localhost:8091/")
    ]
    
    for service_name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                st.success(f"✅ {service_name}: Online")
            else:
                st.error(f"❌ {service_name}: Error ({response.status_code})")
        except:
            st.error(f"❌ {service_name}: Offline")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
if st.session_state.messages:
    st.markdown("### 💭 Chat History")
    for message in st.session_state.messages[-5:]:  # Show last 5 messages
        with st.expander(f"{message['timestamp']} - {message['agent_type']}"):
            st.write(f"**User:** {message['user_message']}")
            st.write(f"**Agent:** {message['agent_response']}")

if __name__ == "__main__":
    main()