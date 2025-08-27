"""
Appointment agent node following the official LangGraph pattern.
"""

import traceback
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import MessagesState
from schemas.intent_analysis import AgentType
from tools.appointment_tools import create_appointment, check_availability, reschedule_appointment
from utils.llm_helpers import create_llm_client
from core.logger import logger

def appointment_agent_node(state: MessagesState) -> MessagesState:
    """Appointment agent node that handles appointment booking and scheduling"""
    
    try:
        logger.info("Appointment agent node starting")
        
        # Get all messages to understand the full conversation context
        if not state["messages"]:
            logger.warning("No messages in state")
            return state
            
        # Get the task description from the supervisor (last message)
        last_message = state["messages"][-1]
        task_description = last_message.get("content", "")
        
        # Get the full conversation context
        conversation_context = ""
        if len(state["messages"]) > 1:
            # Include previous messages for context (skip the supervisor's task description)
            context_messages = state["messages"][:-1]
            conversation_context = "\n".join([
                f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
                for msg in context_messages[-5:]  # Last 5 messages for context
            ])
        
        logger.info(f"Processing appointment task: {task_description[:100]}...")
        
        # Create LLM client
        llm = create_llm_client()
        
        # Create a prompt for appointment handling with tools
        prompt = ChatPromptTemplate.from_template("""
        You are an appointment management agent with access to appointment tools. Your role is to:
        
        1. Handle appointment booking, scheduling, and calendar management
        2. Check availability and create appointments using the available tools
        3. Be helpful and professional
        4. Remember details from the conversation and build upon them
        
        Available tools:
        - create_appointment(date, time, service): Create a new appointment
        - check_availability(date): Check available slots for a date
        - reschedule_appointment(appointment_id, new_date, new_time): Reschedule existing appointment
        
        Previous conversation context:
        {conversation_context}
        
        Current user request: {message}
        
        Instructions:
        - If the user wants to book an appointment, use the create_appointment tool
        - If the user wants to check availability, use the check_availability tool
        - If the user wants to reschedule, use the reschedule_appointment tool
        - If the user is providing additional details for an appointment, acknowledge what you already know and ask for any missing information
        - If this is a new appointment request, ask for the necessary details
        - Be conversational and reference previous parts of the conversation when relevant
        - If the user mentions specific times, dates, or services, acknowledge them
        
        Respond in a helpful, professional manner that builds upon the conversation context.
        """)
        
        # Create the agent with tools
        from langchain.agents import create_react_agent
        from langchain.agents import AgentExecutor
        
        # Get the tools
        tools = [create_appointment, check_availability, reschedule_appointment]
        
        # Create the agent
        agent = create_react_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
        # Generate response
        response = agent_executor.invoke({
            "message": task_description,
            "conversation_context": conversation_context
        })
        
        # Add the response to messages
        state["messages"].append({
            "role": "assistant",
            "content": response["output"]
        })
        
        logger.info("Appointment agent provided response")
        logger.info("Appointment agent node completed successfully")
        return state
        
    except Exception as e:
        logger.error(f"Error in appointment agent node: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


