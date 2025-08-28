"""
Estimate agent sub-graph nodes.

This module contains the agent node for estimate and pricing handling.
"""

import traceback
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from tools.estimate_tools import calculate_estimate, verify_address, get_service_catalog
from utils.llm_helpers import create_llm_client
from core.logger import logger
from .state import State

def estimate_agent(state) -> State:
    """Estimate agent that handles price quotes and estimates"""
    
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
        
        logger.info(f"💰 Estimate agent processing: {task_description[:50]}...")
        
        # Set workflow step if state supports it
        if hasattr(state, 'set_workflow_step'):
            state.set_workflow_step("estimate_calculation")
        
        # Create LLM client
        llm = create_llm_client()
        
        # Get the tools
        tools = [calculate_estimate, verify_address, get_service_catalog]
        
        # Create the agent using LangGraph pattern
        agent = create_react_agent(
            model=llm,
            tools=tools,
            prompt=(
                "You are an estimate agent with access to pricing tools. Your role is to:\n"
                "1. Calculate price estimates for services\n"
                "2. Verify addresses for service areas\n"
                "3. Provide service catalog information\n"
                "4. Be professional and accurate\n\n"
                "Available tools:\n"
                "- calculate_estimate(service_type, address, details): Calculate price estimate\n"
                "- verify_address(address): Verify if address is in service area\n"
                "- get_service_catalog(): Get available services and pricing\n\n"
                "Previous conversation context:\n"
                f"{conversation_context}\n\n"
                "Current user request: {task_description}\n\n"
                "Instructions:\n"
                "- If the user wants a price estimate, use calculate_estimate\n"
                "- If the user provides an address, verify it with verify_address\n"
                "- If the user asks about services, use get_service_catalog\n"
                "- Provide clear, accurate pricing information\n"
                "- Remember details from the conversation and build upon them\n\n"
                "Respond in a helpful, professional manner that builds upon the conversation context."
            ),
            name="estimate_agent"
        )
        
        # Generate response
        response = agent.invoke(state)
        
        logger.info("✅ Estimate agent completed")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in estimate agent: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
