import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
import streamlit as st
from langchain_core.messages import HumanMessage

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from orchestration.graph import get, get_info
from core.logger import logger
from utils.llm_helpers import initialize_langsmith

def process_message(message: str, conversation_history: list = None):
    if conversation_history is None:
        conversation_history = []
    
    try:
        supervisor_graph = get()
        
        initial_messages = []
        
        for msg in conversation_history:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                initial_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        initial_messages.append({"role": "user", "content": message})
        
        initial_state = {
            "messages": initial_messages
        }
        
        results = []
        response_received = False
        
        for chunk in supervisor_graph.stream(initial_state):
            results.append(chunk)
            
            if "messages" in chunk and len(chunk["messages"]) > 0:
                last_message = chunk["messages"][-1]
                if hasattr(last_message, 'type') and last_message.type == "ai":
                    response_received = True
            
            if "messages" in chunk:
                for msg in chunk["messages"]:
                    if hasattr(msg, 'type') and msg.type == "ai" and hasattr(msg, 'content') and msg.content:
                        response_received = True
                        break
            
            for key, value in chunk.items():
                if isinstance(value, dict) and "messages" in value:
                    for msg in value["messages"]:
                        if hasattr(msg, 'type') and msg.type == "ai" and hasattr(msg, 'content') and msg.content:
                            response_received = True
                            break
        
        if not response_received:
            results.append({
                "messages": [{"role": "assistant", "content": "I apologize, but I couldn't process your request. Please try again."}],
                "error": "No response generated"
            })
        
        return results
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return [{"error": str(e)}]

def main():
    st.set_page_config(
        page_title="LangGraph Multi-Agent Supervisor",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 LangGraph Multi-Agent Supervisor System")
    st.markdown("---")
    
    if not os.getenv("OPENAI_API_KEY"):
        st.error("❌ OPENAI_API_KEY environment variable is required")
        st.info("Please set your OpenAI API key in the .env file")
        return
    
    initialize_langsmith()
    
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
    
    for category, questions in predefined_questions.items():
        st.sidebar.subheader(category)
        for question in questions:
            if st.sidebar.button(question, key=f"btn_{category}_{question[:20]}"):
                st.session_state.user_input = question
    
    st.header("💬 Chat Interface")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            if "metadata" in message and message["metadata"]:
                with st.expander("🔍 Additional Details"):
                    st.json(message["metadata"])
    
    user_input = st.chat_input("Type your message here...")
    
    if "user_input" in st.session_state:
        user_input = st.session_state.user_input
        del st.session_state.user_input
    
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.write(user_input)
        
        with st.chat_message("assistant"):
            with st.spinner("🤖 Processing your request..."):
                try:
                    results = process_message(user_input, st.session_state.conversation_history)
                    
                    final_response = None
                    metadata = {}
                    
                    for result in results:
                        if "messages" in result and len(result["messages"]) > 0:
                            last_message = result["messages"][-1]
                            if hasattr(last_message, 'type') and last_message.type == "ai":
                                final_response = last_message.content
                        
                        for key, value in result.items():
                            if isinstance(value, dict) and "messages" in value:
                                for msg in value["messages"]:
                                    if hasattr(msg, 'type') and msg.type == "ai" and hasattr(msg, 'content') and msg.content:
                                        final_response = msg.content
                                        break
                    
                    if final_response:
                        st.write(final_response)
                    else:
                        st.error("❌ No response generated")
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": final_response or "Sorry, I couldn't process your request."
                    })
                    
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
    
    if st.sidebar.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.header("ℹ️ System Info")
    
    try:
        graph_info = get_info()
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
    
    if st.session_state.conversation_history:
        st.sidebar.metric(
            "Conversation Length", 
            len(st.session_state.conversation_history)
        )

if __name__ == "__main__":
    main()
