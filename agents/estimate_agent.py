"""
Estimate agent node following the official LangGraph pattern.
"""

import traceback
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from schemas.intent_analysis import AgentType
from tools.estimate_tools import calculate_estimate, verify_address, get_service_catalog
from utils.llm_helpers import create_llm_client
from core.logger import logger

def estimate_agent_node(state: MessagesState) -> MessagesState:
    """Estimate agent node that handles price quotes and cost estimates"""
    
    try:
        logger.info("Estimate agent node starting")
        
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
        
        logger.info(f"Processing estimate task: {task_description[:100]}...")
        
        # Create LLM client
        llm = create_llm_client()
        
        # Get the tools
        tools = [calculate_estimate, verify_address, get_service_catalog]
        
        # Create the agent using LangGraph pattern
        agent = create_react_agent(
            model=llm,
            tools=tools,
            prompt=(
                "You are an estimate agent with access to estimate tools. Your role is to:\n"
                "1. Handle price quotes, cost estimates, and pricing information\n"
                "2. Provide accurate pricing for services using the available tools\n"
                "3. Be professional and helpful\n"
                "4. Remember details from the conversation and build upon them\n\n"
                "Available tools:\n"
                "- calculate_estimate(service, location): Calculate service estimate\n"
                "- verify_address(address): Verify if address is in service area\n"
                "- get_service_catalog(): Get available services catalog\n\n"
                "Previous conversation context:\n"
                f"{conversation_context}\n\n"
                "Current user request: {task_description}\n\n"
                "Instructions:\n"
                "- If the user wants a price quote, use the calculate_estimate tool\n"
                "- If the user provides an address, use the verify_address tool\n"
                "- If the user asks about available services, use the get_service_catalog tool\n"
                "- If the user is providing additional details for an estimate, acknowledge what you already know and ask for any missing information\n"
                "- If this is a new estimate request, ask for the necessary details\n"
                "- Be professional and reference previous parts of the conversation when relevant\n"
                "- If the user mentions specific services, locations, or requirements, acknowledge them\n\n"
                "Respond in a professional, helpful manner that builds upon the conversation context."
            ),
            name="estimate_agent"
        )
        
        # Generate response
        response = agent.invoke(state)
        
        logger.info("Estimate agent provided response")
        logger.info("Estimate agent node completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error in estimate agent node: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


