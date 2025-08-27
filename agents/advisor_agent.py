"""
Advisor agent node following the official LangGraph pattern.
"""

import traceback
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from schemas.intent_analysis import AgentType
from tools.advisor_tools import get_service_info, get_business_hours, get_contact_info
from utils.llm_helpers import create_llm_client
from core.logger import logger

def advisor_agent_node(state: MessagesState) -> MessagesState:
    """Advisor agent node that handles business information and recommendations"""
    
    try:
        logger.info("Advisor agent node starting")
        
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
        
        logger.info(f"Processing advisor task: {task_description[:100]}...")
        
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
                "1. Provide business information, service details, and recommendations\n"
                "2. Answer questions about company services and policies using the available tools\n"
                "3. Be knowledgeable and helpful\n"
                "4. Remember details from the conversation and build upon them\n\n"
                "Available tools:\n"
                "- get_service_info(service): Get detailed information about a specific service\n"
                "- get_business_hours(): Get business hours information\n"
                "- get_contact_info(): Get contact information\n\n"
                "Previous conversation context:\n"
                f"{conversation_context}\n\n"
                "Current user request: {task_description}\n\n"
                "Instructions:\n"
                "- If the user asks about a specific service, use the get_service_info tool\n"
                "- If the user asks about business hours, use the get_business_hours tool\n"
                "- If the user asks for contact information, use the get_contact_info tool\n"
                "- If the user is asking follow-up questions about previously discussed services, reference the earlier conversation\n"
                "- If this is a new inquiry, provide comprehensive information\n"
                "- Be knowledgeable and reference previous parts of the conversation when relevant\n"
                "- If the user mentions specific services, policies, or previous discussions, acknowledge them\n\n"
                "Respond in a knowledgeable, helpful manner that builds upon the conversation context."
            ),
            name="advisor_agent"
        )
        
        # Generate response
        response = agent.invoke(state)
        
        logger.info("Advisor agent provided response")
        logger.info("Advisor agent node completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error in advisor agent node: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


