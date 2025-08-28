"""
Advisor agent sub-graph nodes.

This module contains the agent node for business information and recommendations.
"""

import traceback
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from tools.advisor_tools import get_service_info, get_business_hours, get_contact_info
from utils.llm_helpers import create_llm_client
from core.logger import logger
from .state import State

def advisor_agent(state) -> State:
    """Advisor agent that provides business information and recommendations"""
    
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
        
        logger.info(f"📋 Advisor agent processing: {task_description[:50]}...")
        
        # Set workflow step if state supports it
        if hasattr(state, 'set_workflow_step'):
            state.set_workflow_step("business_advice")
        
        # Create LLM client
        llm = create_llm_client()
        
        # Get the tools
        tools = [get_service_info, get_business_hours, get_contact_info]
        
        # Create the agent using LangGraph pattern
        agent = create_react_agent(
            model=llm,
            tools=tools,
            prompt=(
                "You are an advisor agent with access to business information tools. Your role is to:\n"
                "1. Provide business information and recommendations\n"
                "2. Share service details and capabilities\n"
                "3. Provide business hours and contact information\n"
                "4. Be knowledgeable and helpful\n\n"
                "Available tools:\n"
                "- get_service_info(service_type): Get detailed service information\n"
                "- get_business_hours(): Get current business hours\n"
                "- get_contact_info(): Get contact information\n\n"
                "Previous conversation context:\n"
                f"{conversation_context}\n\n"
                "Current user request: {task_description}\n\n"
                "Instructions:\n"
                "- If the user asks about services, use get_service_info\n"
                "- If the user asks about hours, use get_business_hours\n"
                "- If the user asks about contact info, use get_contact_info\n"
                "- Provide helpful recommendations based on user needs\n"
                "- Remember details from the conversation and build upon them\n\n"
                "Respond in a helpful, professional manner that builds upon the conversation context."
            ),
            name="advisor_agent"
        )
        
        # Generate response
        response = agent.invoke(state)
        
        logger.info("✅ Advisor agent completed")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in advisor agent: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
