"""
General agent sub-graph nodes.

This module contains the agent node for general conversation handling.
"""

import traceback
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from utils.llm_helpers import create_llm_client
from core.logger import logger
from .state import State

def general_agent(state) -> State:
    """General agent that handles casual conversation and greetings"""
    
    try:
        # Get all messages to understand the full conversation context
        if not state["messages"]:
            logger.warning("No messages in state")
            return state
            
        # Get the task description from the supervisor (last message)
        last_message = state["messages"][-1]
        task_description = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        # Get the full conversation context
        conversation_context = ""
        if len(state["messages"]) > 1:
            # Include previous messages for context (skip the supervisor's task description)
            context_messages = state["messages"][:-1]
            conversation_context = "\n".join([
                f"{msg.type if hasattr(msg, 'type') else 'unknown'}: {msg.content if hasattr(msg, 'content') else str(msg)}"
                for msg in context_messages[-5:]  # Last 5 messages for context
            ])
        
        logger.info(f"🤖 General agent processing: {task_description[:50]}...")
        
        # Set workflow step if state supports it
        if hasattr(state, 'set_workflow_step'):
            state.set_workflow_step("general_conversation")
        
        # Create LLM client
        llm = create_llm_client()
        
        # Create the agent using LangGraph pattern
        agent = create_react_agent(
            model=llm,
            tools=[],  # No tools needed for general conversation
            prompt=(
                "You are a friendly and helpful general conversation agent. Your role is to:\n"
                "1. Handle casual conversation, greetings, and general inquiries\n"
                "2. Be warm, welcoming, and engaging\n"
                "3. Remember details from the conversation and build upon them\n"
                "4. Help users feel comfortable and heard\n\n"
                "Previous conversation context:\n"
                f"{conversation_context}\n\n"
                "Current user request: {task_description}\n\n"
                "Instructions:\n"
                "- Be conversational and friendly\n"
                "- Reference previous parts of the conversation when relevant\n"
                "- If the user asks about specific services, politely redirect them to the appropriate agent\n"
                "- Keep responses engaging but concise\n"
                "- Show genuine interest in the user's needs\n\n"
                "Respond in a warm, helpful manner that builds upon the conversation context."
            ),
            name="general_agent"
        )
        
        # Generate response
        response = agent.invoke(state)
        
        logger.info("✅ General agent completed")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in general agent: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
