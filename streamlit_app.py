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

def process_message(current_state=None):
    """Process a single message through the graph"""
    try:
        # Initialize or use existing state
        if current_state is None:
            current_state = create_state()
        
        logger.info(f"Current state: {current_state}")


        # Ensure the state has the proper structure
        if "messages" not in current_state:
            current_state["messages"] = []
        
        logger.info(f"Starting graph execution with {len(current_state['messages'])} messages")
        
        # Get graph and process
        graph = get_graph()
        the_response = ""
        the_agent = "Unknown"
        
        for chunk in graph.stream(current_state):
            
            # Always update final_state to the latest chunk
            final_state = chunk
            
            logger.info(f"Processing chunk with keys: {list(chunk.keys())}")
            if "messages" in chunk:
                logger.info(f"Chunk has {len(chunk['messages'])} messages")
            
            # Check for any agent response in the chunk
            for agent_name, state in chunk.items():

                logger.info(f"Agent name: {agent_name}")
                logger.info(f"State: {state}")
                
                if state and isinstance(state, dict):
                    messages = state.get("messages", [])
                    if len(messages) > 0:
                        last_message = messages[-1]
                        the_response = last_message
                        the_agent = agent_name

        return the_response, the_agent
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return "Error processing message", "Error"

def main():
    st.title("🤖 Multi-Agent Orchestration System")
    st.markdown("---")
    
    # Initialize session state
    if "graph_state" not in st.session_state:
        st.session_state.graph_state = create_state()
    
    the_messages = st.session_state.graph_state['messages']
    the_current = st.session_state.graph_state['current']

    logger.info(f"Messages: {the_messages}")
    logger.info(f"Current: {the_current}")
    
    # Initialize system on first run
    if st.session_state.graph_state is None:
        with st.spinner("Initializing system..."):
            initialize_langsmith()
            st.session_state.graph_state = create_state()

    logger.info(f"Messages: {the_messages}")
    
    # Display chat messages
    for message in the_messages:
        if message.type == "human":
            st.chat_message("user").write(message.content)
        else:
            # Check if this is a tool response
            if "Tool Response:" in message.content:
                # Display tool responses with a different style
                with st.chat_message("assistant"):
                    st.markdown("🔧 **Tool Response**")
                    st.write(message.content.replace("Tool Response: ", ""))
            else:
                st.chat_message("assistant").write(message.content)
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat
        the_messages.append(HumanMessage(content=prompt))
        st.chat_message("user").write(prompt)
        
        # Process message
        with st.spinner("Processing..."):
            response, agent_name = process_message(
                st.session_state.graph_state
            )
        
        # Add assistant response to chat
        the_messages.append(response)
        the_current = agent_name

        # print messages
        st.chat_message("assistant").write(f"**{agent_name}**: {response.content}")

        st.session_state.graph_state["messages"] = the_messages
        st.session_state.graph_state["current"] = the_current
    
    logger.info(f"Messages: {the_messages}")

    # Sidebar with controls
    with st.sidebar:
        st.header("Controls")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            the_messages = []
            the_current = "start"
            st.session_state.graph_state = create_state()
            st.rerun()
        
        # Show current state info
        st.header("System Info")
        if st.session_state.graph_state:
            st.write(f"Messages in state: {len(st.session_state.graph_state.get('messages', []))}")
            st.write(f"Current agent: {st.session_state.graph_state.get('current', 'N/A')}")
            st.write(f"Chat messages: {len(the_messages)}")
            
            # Show message types in current state
            if "messages" in st.session_state.graph_state:
                message_types = []
                for msg in st.session_state.graph_state["messages"]:
                    if hasattr(msg, 'type'):
                        message_types.append(msg.type)
                if message_types:
                    st.write(f"Message types: {', '.join(message_types[-5:])}")  # Show last 5
        
        
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
