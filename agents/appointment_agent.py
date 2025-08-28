"""
Appointment agent node following the official LangGraph pattern.
"""

import traceback
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from schemas.intent_analysis import AgentType
from tools.appointment_tools import create_appointment, check_availability, reschedule_appointment
from utils.llm_helpers import create_llm_client
from core.logger import logger

def appointment_agent_node(state: MessagesState) -> MessagesState:
    """Appointment agent node that handles appointment booking and scheduling"""
    
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
        
        logger.info(f"📅 Appointment agent processing: {task_description[:50]}...")
        
        # Create LLM client
        llm = create_llm_client()
        
        # Get the tools
        tools = [create_appointment, check_availability, reschedule_appointment]
        
        # Create the agent using LangGraph pattern
        agent = create_react_agent(
            model=llm,
            tools=tools,
            prompt=(
                "You are an appointment management agent with access to appointment tools. Your role is to:\n"
                "1. Handle appointment booking, scheduling, and calendar management\n"
                "2. Check availability and create appointments using the available tools\n"
                "3. Be helpful and professional\n"
                "4. Remember details from the conversation and build upon them\n\n"
                "Available tools:\n"
                "- create_appointment(date, time, service): Create a new appointment\n"
                "- check_availability(date): Check available slots for a date\n"
                "- reschedule_appointment(appointment_id, new_date, new_time): Reschedule existing appointment\n\n"
                "Previous conversation context:\n"
                f"{conversation_context}\n\n"
                "Current user request: {task_description}\n\n"
                "Instructions:\n"
                "- If the user wants to book an appointment, use the create_appointment tool\n"
                "- If the user wants to check availability, use the check_availability tool\n"
                "- If the user wants to reschedule, use the reschedule_appointment tool\n"
                "- If the user is providing additional details for an appointment, acknowledge what you already know and ask for any missing information\n"
                "- If this is a new appointment request, ask for the necessary details\n"
                "- Be conversational and reference previous parts of the conversation when relevant\n"
                "- If the user mentions specific times, dates, or services, acknowledge them\n\n"
                "Respond in a helpful, professional manner that builds upon the conversation context."
            ),
            name="appointment_agent"
        )
        
        # Generate response
        response = agent.invoke(state)
        
        logger.info("✅ Appointment agent completed")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in appointment agent: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


