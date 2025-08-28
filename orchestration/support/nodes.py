"""
Support agent sub-graph nodes.

This module contains the agent node for support ticket and warranty claim handling.
"""

import traceback
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from tools.support_tools import create_support_ticket, check_warranty_status, escalate_ticket
from utils.llm_helpers import create_llm_client
from core.logger import logger
from .state import State

def support_agent(state) -> State:
    """Support agent that handles customer support and warranty claims"""
    
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
        
        logger.info(f"🎫 Support agent processing: {task_description[:50]}...")
        
        # Set workflow step if state supports it
        if hasattr(state, 'set_workflow_step'):
            state.set_workflow_step("support_handling")
        
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
                "1. Handle customer support requests and warranty claims\n"
                "2. Create support tickets for issues\n"
                "3. Check warranty status for products\n"
                "4. Escalate issues when necessary\n"
                "5. Be empathetic and professional\n\n"
                "Available tools:\n"
                "- create_support_ticket(issue_type, description, priority): Create a new support ticket\n"
                "- check_warranty_status(product_id): Check warranty status for a product\n"
                "- escalate_ticket(ticket_id, reason): Escalate an existing ticket\n\n"
                "Previous conversation context:\n"
                f"{conversation_context}\n\n"
                "Current user request: {task_description}\n\n"
                "Instructions:\n"
                "- If the user has a support issue, use create_support_ticket\n"
                "- If the user wants to check warranty, use check_warranty_status\n"
                "- If an issue needs escalation, use escalate_ticket\n"
                "- Be empathetic and understanding of customer frustrations\n"
                "- Provide clear next steps and expectations\n"
                "- Remember details from the conversation and build upon them\n\n"
                "Respond in a helpful, professional manner that builds upon the conversation context."
            ),
            name="support_agent"
        )
        
        # Generate response
        response = agent.invoke(state)
        
        logger.info("✅ Support agent completed")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in support agent: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
