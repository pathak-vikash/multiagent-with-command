#!/usr/bin/env python3
"""
Simple Streamlit App for LangGraph Multi-Agent Orchestration System
"""

import os
import sys
from pathlib import Path
import streamlit as st
from datetime import datetime
from core.logger import logger

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from orchestration.graph import get as get_graph
from orchestration.state import create as create_state
from utils.llm_helpers import initialize_langsmith
from langchain_core.messages import HumanMessage

def process_message(message: str, current_state=None):
    """Process a single message through the graph"""
    try:
        # Initialize or use existing state
        if current_state is None:
            current_state = create_state()
        
        # Ensure the state has the proper structure
        if "messages" not in current_state:
            current_state["messages"] = []
        
        # Add the new user message to the existing conversation
        current_state["messages"].append(HumanMessage(content=message))
        
        # Get graph and process
        graph = get_graph()
        response = "No response generated"
        final_state = current_state
        current_agent = "Unknown"
        response_chunk = None
        
        for chunk in graph.stream(current_state):
            # Store the last chunk for debugging
            st.session_state.last_chunk = chunk
            
            # Check for any agent response in the chunk
            for key, value in chunk.items():
                try:
                    if isinstance(value, dict):
                        # Check if this agent has messages
                        if "messages" in value and len(value["messages"]) > 0:
                            # Get the last AI message from this agent
                            last_message = value["messages"][-1]
                            if hasattr(last_message, 'type') and last_message.type == "ai":
                                response = last_message.content
                                current_agent = key  # The key is the agent name
                                final_state = chunk
                                response_chunk = chunk
                                break
                        
                        # Also check if the value itself is a message
                        elif hasattr(value, 'type') and value.type == "ai":
                            response = value.content
                            current_agent = key
                            final_state = chunk
                            response_chunk = chunk
                            break
                    
                    # Check if the value itself is an AI message
                    elif hasattr(value, 'type') and value.type == "ai":
                        response = value.content
                        current_agent = key
                        final_state = chunk
                        response_chunk = chunk
                        break
                        
                except Exception as e:
                    # Log the error but continue processing other keys
                    continue
            
            # If we found a response, break out of the outer loop
            if response != "No response generated":
                break
            
            # Update final state
            final_state = chunk
        
        # Store the response chunk for debugging
        if response_chunk:
            st.session_state.last_chunk = response_chunk
        
        # Ensure the final state preserves all messages
        if final_state and "messages" in final_state:
            pass  # State is good
        else:
            final_state = current_state
        
        return response, final_state, current_agent
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return "Error processing message", current_state, "Error"

def main():
    st.title("🤖 Multi-Agent Orchestration System")
    st.markdown("---")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "graph_state" not in st.session_state:
        st.session_state.graph_state = None
    
    if "last_chunk" not in st.session_state:
        st.session_state.last_chunk = None
    
    # Initialize system on first run
    if st.session_state.graph_state is None:
        with st.spinner("Initializing system..."):
            initialize_langsmith()
            st.session_state.graph_state = create_state()
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        # Process message
        with st.spinner("Processing..."):
            response, st.session_state.graph_state, agent_name = process_message(
                prompt, 
                st.session_state.graph_state
            )
        
        # Add assistant response to chat
        st.session_state.messages.append({"role": "assistant", "content": f"**{agent_name}**: {response}"})
        st.chat_message("assistant").write(f"**{agent_name}**: {response}")
    
    # Sidebar with controls
    with st.sidebar:
        st.header("Controls")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.session_state.graph_state = create_state()
            st.session_state.last_chunk = None
            st.rerun()
        
        # Show current state info
        st.header("System Info")
        if st.session_state.graph_state:
            st.write(f"Messages in state: {len(st.session_state.graph_state.get('messages', []))}")
            st.write(f"Current agent: {st.session_state.graph_state.get('current', 'N/A')}")
            st.write(f"Chat messages: {len(st.session_state.messages)}")
        
        # Debug: Show last chunk details
        if st.session_state.last_chunk:
            st.header("Debug: Last Chunk")
            with st.expander("View chunk details"):
                st.json(st.session_state.last_chunk)
        
        # Help section
        st.header("Help")
        st.markdown("""
        **Example messages:**
        - "Hello! How are you today?"
        - "I need to book an appointment"
        - "My warranty claim was denied"
        - "What services do you offer?"
        - "Can you give me a quote?"
        """)

if __name__ == "__main__":
    main()
