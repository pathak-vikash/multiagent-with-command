import streamlit as st
import os
import json
import logging
import traceback
from datetime import datetime
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Import our centralized graph module
from graph import get_supervisor_graph, get_graph_info
from core.logger import logger

# Load environment variables
load_dotenv()

def process_message(message: str, conversation_history: list = None):
    """Process a single message through the supervisor system"""
    if conversation_history is None:
        conversation_history = []
    
    try:
        logger.info(f"Processing message: {message[:100]}...")
        
        # Get the supervisor graph from centralized module
        supervisor_graph = get_supervisor_graph()
        
        # Build the initial state from conversation history
        initial_messages = []
        
        # Add conversation history to messages
        for msg in conversation_history:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                initial_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add the current message
        initial_messages.append({"role": "user", "content": message})
        
        # Create the initial state using MessagesState format
        initial_state = {
            "messages": initial_messages
        }
        
        logger.info(f"Initial state has {len(initial_messages)} messages")
        logger.info("Starting graph execution")
        
        # Stream the conversation and collect all results
        results = []
        response_received = False
        
        for chunk in supervisor_graph.stream(initial_state):
            results.append(chunk)
            
            # Check if we have a final response
            if "messages" in chunk and len(chunk["messages"]) > 0:
                last_message = chunk["messages"][-1]
                if last_message["role"] == "assistant":
                    response_received = True
                    logger.info(f"Response received: {last_message['content'][:100]}...")
            
            # Also check for any assistant messages in the entire chunk
            if "messages" in chunk:
                for msg in chunk["messages"]:
                    if msg.get("role") == "assistant" and msg.get("content"):
                        response_received = True
                        logger.info(f"Response found in chunk: {msg['content'][:100]}...")
                        break
            
            # Check for nested messages in agent chunks (e.g., general_agent, appointment_agent, etc.)
            for key, value in chunk.items():
                if isinstance(value, dict) and "messages" in value:
                    for msg in value["messages"]:
                        if msg.get("role") == "assistant" and msg.get("content"):
                            response_received = True
                            logger.info(f"Response found in {key} chunk: {msg['content'][:100]}...")
                            break
        
        logger.info(f"Graph execution completed. Response received: {response_received}")
        logger.info(f"Total chunks received: {len(results)}")
        
        # If no response was received, add a fallback
        if not response_received:
            logger.warning("No response received from graph, adding fallback")
            results.append({
                "messages": [{"role": "assistant", "content": "I apologize, but I couldn't process your request. Please try again."}],
                "error": "No response generated"
            })
        
        return results
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return [{"error": str(e)}]

def main():
    st.set_page_config(
        page_title="LangGraph Multi-Agent Supervisor",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 LangGraph Multi-Agent Supervisor System")
    st.markdown("---")
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        st.error("❌ OPENAI_API_KEY environment variable is required")
        st.info("Please set your OpenAI API key in the .env file")
        return
    
    # Sidebar with predefined questions
    st.sidebar.header("💡 Predefined Questions")
    st.sidebar.markdown("Click any question to use it:")
    
    predefined_questions = {
        "General": [
            "Hi there! How are you doing today?",
            "Thanks for your help, you've been great!",
            "What's the weather like today? Just curious!"
        ],
        "Appointments": [
            "I need to book an appointment for lawn care next Tuesday afternoon",
            "Can you check availability for house cleaning on Friday?",
            "I want to reschedule my appointment for next week"
        ],
        "Support": [
            "My warranty claim was denied and I'm really frustrated about it",
            "I have a problem with my recent service",
            "Can you help me with a technical issue?"
        ],
        "Estimates": [
            "Can you give me a quote for cleaning services at 123 Main Street?",
            "I need an estimate for landscaping work",
            "What's the cost for pest control services?"
        ],
        "Information": [
            "What services do you offer and what are your business hours?",
            "Tell me about your lawn care services",
            "How can I contact your support team?"
        ]
    }
    
    # Display predefined questions by category
    for category, questions in predefined_questions.items():
        st.sidebar.subheader(category)
        for question in questions:
            if st.sidebar.button(question, key=f"btn_{category}_{question[:20]}"):
                st.session_state.user_input = question
    
    # Main chat interface
    st.header("💬 Chat Interface")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # Display additional information if available
            if "metadata" in message and message["metadata"]:
                with st.expander("🔍 Additional Details"):
                    st.json(message["metadata"])
    
    # User input
    user_input = st.chat_input("Type your message here...")
    
    # Check if a predefined question was selected
    if "user_input" in st.session_state:
        user_input = st.session_state.user_input
        del st.session_state.user_input
    
    if user_input:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Process the message
        with st.chat_message("assistant"):
            with st.spinner("🤖 Processing your request..."):
                try:
                    results = process_message(user_input, st.session_state.conversation_history)
                    
                    # Find the final response
                    final_response = None
                    metadata = {}
                    
                    for result in results:
                        if "messages" in result and len(result["messages"]) > 0:
                            last_message = result["messages"][-1]
                            if last_message["role"] == "assistant":
                                final_response = last_message["content"]
                        
                        # Check for nested messages in agent chunks
                        for key, value in result.items():
                            if isinstance(value, dict) and "messages" in value:
                                for msg in value["messages"]:
                                    if msg.get("role") == "assistant" and msg.get("content"):
                                        final_response = msg["content"]
                                        break
                    
                    if final_response:
                        st.write(final_response)
                    else:
                        st.error("❌ No response generated")
                    
                    # Add assistant response to chat
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": final_response or "Sorry, I couldn't process your request."
                    })
                    
                    # Update conversation history with both user and assistant messages
                    st.session_state.conversation_history.append({
                        "role": "user",
                        "content": user_input,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    if final_response:
                        st.session_state.conversation_history.append({
                            "role": "assistant",
                            "content": final_response,
                            "timestamp": datetime.now().isoformat()
                        })
                    
                except Exception as e:
                    st.error(f"❌ Error processing message: {e}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "Sorry, I encountered an error processing your request. Please try again."
                    })
    
    # Clear chat button
    if st.sidebar.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.rerun()
    
    # System information
    st.sidebar.markdown("---")
    st.sidebar.header("ℹ️ System Info")
    
    # Get graph information
    try:
        graph_info = get_graph_info()
        st.sidebar.markdown(f"**Graph Nodes:** {len(graph_info['nodes'])}")
        st.sidebar.markdown(f"**Routing:** {graph_info['routing_method']}")
        
        st.sidebar.markdown("**Available Agents:**")
        for agent, description in graph_info["agent_types"].items():
            emoji = {
                "general_agent": "🤖",
                "appointment_agent": "📅", 
                "support_agent": "🎫",
                "estimate_agent": "💰",
                "advisor_agent": "📋"
            }.get(agent, "🤖")
            st.sidebar.markdown(f"- {emoji} {agent.replace('_', ' ').title()}: {description}")
    except Exception as e:
        st.sidebar.error(f"Error loading graph info: {e}")
    
    # Display conversation history length
    if st.session_state.conversation_history:
        st.sidebar.metric(
            "Conversation Length", 
            len(st.session_state.conversation_history)
        )

if __name__ == "__main__":
    main()
