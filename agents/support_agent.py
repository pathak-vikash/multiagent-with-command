"""
Support agent node following the official LangGraph pattern.
"""

import traceback
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from schemas.intent_analysis import AgentType
from tools.support_tools import create_support_ticket, check_warranty_status, escalate_ticket
from utils.llm_helpers import create_llm_client
from core.logger import logger

def support_agent_node(state: MessagesState) -> MessagesState:
    """Support agent node that handles customer support and warranty claims"""
    
    try:
        logger.info("Support agent node starting")
        
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
        
        logger.info(f"Processing support task: {task_description[:100]}...")
        
        # Create LLM client
        llm = create_llm_client()
        
        # Get the tools
        tools = [create_support_ticket, check_warranty_status, escalate_ticket]
        
        # Create the agent using LangGraph pattern
        agent = create_react_agent(
            model=llm,
            tools=tools,
            prompt=(
                "You are a customer support agent with access to support tools. Your role is to:\n"
                "1. Handle customer support issues, warranty claims, and technical problems\n"
                "2. Create support tickets and track issues using the available tools\n"
                "3. Be empathetic and helpful\n"
                "4. Remember details from the conversation and build upon them\n\n"
                "Available tools:\n"
                "- create_support_ticket(issue, priority): Create a new support ticket\n"
                "- check_warranty_status(customer_id): Check warranty status for a customer\n"
                "- escalate_ticket(ticket_id, reason): Escalate a support ticket\n\n"
                "Previous conversation context:\n"
                f"{conversation_context}\n\n"
                "Current user request: {task_description}\n\n"
                "Instructions:\n"
                "- If the user has a support issue, use the create_support_ticket tool\n"
                "- If the user wants to check warranty status, use the check_warranty_status tool\n"
                "- If the user wants to escalate an issue, use the escalate_ticket tool\n"
                "- If the user is providing additional details about their issue, acknowledge what you already know\n"
                "- If this is a new support request, ask for the necessary details\n"
                "- Be empathetic and reference previous parts of the conversation when relevant\n"
                "- If the user mentions specific problems, services, or previous interactions, acknowledge them\n\n"
                "Respond in an empathetic, helpful manner that builds upon the conversation context."
            ),
            name="support_agent"
        )
        
        # Generate response
        response = agent.invoke(state)
        
        logger.info("Support agent provided response")
        logger.info("Support agent node completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error in support agent node: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


