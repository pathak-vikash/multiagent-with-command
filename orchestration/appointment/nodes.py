"""
Appointment sub-graph nodes.

This module contains all the agent nodes for the appointment booking workflow:
1. SOP Collector Agent - Collects and validates all 5 SOPs
2. Appointment Booking Agent - Handles the actual booking after SOPs are complete
"""

import traceback
import re
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from tools.appointment_tools import create_appointment, check_availability, reschedule_appointment
from utils.llm_helpers import create_llm_client
from core.logger import logger
from .state import AppointmentState

def sop_collector(state) -> AppointmentState:
    """SOP Collector agent that ensures all 5 SOPs are completed before appointment booking"""
    
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
        
        logger.info(f"📋 SOP Collector agent processing: {task_description[:50]}...")
        
        # Set workflow step if state supports it
        if hasattr(state, 'set_workflow_step'):
            state.set_workflow_step("sop_collection")
        
        # Create LLM client
        llm = create_llm_client()
        
        # Create the agent using LangGraph pattern
        agent = create_react_agent(
            model=llm,
            tools=[],  # No tools needed for SOP collection
            prompt=(
                "You are a SOP (Standard Operating Procedure) Collector agent. Your role is to ensure ALL 5 SOPs are completed before any appointment can be booked.\n\n"
                "CRITICAL: You must collect and validate these 5 SOPs in order:\n\n"
                "1. **AGENDA:** Ask the user to clearly state the purpose of the appointment.\n"
                "   - What is the main reason for this appointment?\n"
                "   - What specific issue or service do they need?\n\n"
                "2. **SERVICE:** Based on the agenda, determine the type of service.\n"
                "   - If unsure, present this list and ask user to select:\n"
                "     * inspection, repair, maintenance, installation, replacement, consultation, other\n"
                "   - Validate that the service type is from the allowed list\n\n"
                "3. **TIMING:** Collect preferred dates and time.\n"
                "   - Ask for specific date and time preferences\n"
                "   - Ensure the date and time are in the future, not the past\n"
                "   - Format should be YYYY-MM-DD HH:MM\n\n"
                "4. **LOCATION:** Confirm service location.\n"
                "   - If user already shared location in context or profile, use and confirm that location\n"
                "   - If not shared, ask for location (city, state, or country)\n\n"
                "5. **CONTACT:** Confirm user communication preferences.\n"
                "   - Ask for email or phone number for appointment details and updates\n"
                "   - Validate the contact format\n\n"
                "Previous conversation context:\n"
                f"{conversation_context}\n\n"
                "Current user request: {task_description}\n\n"
                "Instructions:\n"
                "- Systematically go through each SOP one by one\n"
                "- If any SOP information is missing, ask for it specifically\n"
                "- If user provides multiple SOPs at once, acknowledge all and ask for any missing ones\n"
                "- Be conversational and reference previous parts of the conversation when relevant\n"
                "- Validate each piece of information as it's provided\n"
                "- Once ALL 5 SOPs are confirmed, summarize them and indicate readiness for booking\n"
                "- Do NOT proceed to booking - that's handled by a separate agent\n"
                "- If user tries to skip SOPs, politely insist on completing them\n\n"
                "Response format when all SOPs are complete:\n"
                "✅ All SOPs collected successfully!\n"
                "📋 Agenda: [purpose]\n"
                "🔧 Service: [service_type]\n"
                "📅 Date: [date]\n"
                "🕐 Time: [time]\n"
                "📍 Location: [location]\n"
                "📞 Contact: [contact]\n\n"
                "Ready to proceed with appointment booking.\n\n"
                "Respond in a helpful, professional manner that builds upon the conversation context."
            ),
            name="sop_collector_agent"
        )
        
        # Generate response
        response = agent.invoke(state)
        
        logger.info("✅ SOP Collector agent completed")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in SOP Collector agent: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

def extract_sop_info_from_context(messages):
    """Extract SOP information from conversation context"""
    sop_info = {
        'agenda': None,
        'service': None,
        'date': None,
        'time': None,
        'location': None,
        'contact': None
    }
    
    # Look for SOP summary in recent messages
    for msg in reversed(messages[-3:]):  # Check last 3 messages
        content = msg.content if hasattr(msg, 'content') else str(msg)
        
        # Look for SOP summary pattern
        if "✅ All SOPs collected successfully!" in content:
            # Extract information using regex patterns
            agenda_match = re.search(r'📋 Agenda: (.+)', content)
            if agenda_match:
                sop_info['agenda'] = agenda_match.group(1).strip()
            
            service_match = re.search(r'🔧 Service: (.+)', content)
            if service_match:
                sop_info['service'] = service_match.group(1).strip()
            
            date_match = re.search(r'📅 Date: (.+)', content)
            if date_match:
                sop_info['date'] = date_match.group(1).strip()
            
            time_match = re.search(r'🕐 Time: (.+)', content)
            if time_match:
                sop_info['time'] = time_match.group(1).strip()
            
            location_match = re.search(r'📍 Location: (.+)', content)
            if location_match:
                sop_info['location'] = location_match.group(1).strip()
            
            contact_match = re.search(r'📞 Contact: (.+)', content)
            if contact_match:
                sop_info['contact'] = contact_match.group(1).strip()
            
            break
    
    return sop_info

def booking_agent(state) -> AppointmentState:
    """Appointment Booking agent that handles the actual booking after SOPs are collected"""
    
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
        
        logger.info(f"📅 Appointment Booking agent processing: {task_description[:50]}...")
        
        # Set workflow step if state supports it
        if hasattr(state, 'set_workflow_step'):
            state.set_workflow_step("appointment_booking")
        
        # Extract SOP information from conversation context
        sop_info = extract_sop_info_from_context(state["messages"])
        
        # Store SOP data in state if state supports it
        if hasattr(state, 'set_sop_data'):
            for key, value in sop_info.items():
                if value:
                    state.set_sop_data(key, value)
        
        # Create LLM client
        llm = create_llm_client()
        
        # Get the tools
        tools = [create_appointment, check_availability, reschedule_appointment]
        
        # Create the agent using LangGraph pattern
        agent = create_react_agent(
            model=llm,
            tools=tools,
            prompt=(
                "You are an Appointment Booking agent. Your role is to handle the actual appointment booking process AFTER all SOPs have been collected and validated.\n\n"
                "Available tools:\n"
                "- create_appointment(date, time, service, agenda, location, contact): Create a new appointment with all SOP information\n"
                "- check_availability(date): Check available slots for a date\n"
                "- reschedule_appointment(appointment_id, new_date, new_time): Reschedule existing appointment\n\n"
                "Previous conversation context:\n"
                f"{conversation_context}\n\n"
                "Current user request: {task_description}\n\n"
                "Extracted SOP information from context:\n"
                f"- Agenda: {sop_info['agenda'] or 'Not found'}\n"
                f"- Service: {sop_info['service'] or 'Not found'}\n"
                f"- Date: {sop_info['date'] or 'Not found'}\n"
                f"- Time: {sop_info['time'] or 'Not found'}\n"
                f"- Location: {sop_info['location'] or 'Not found'}\n"
                f"- Contact: {sop_info['contact'] or 'Not found'}\n\n"
                "Instructions:\n"
                "- If all SOP information is available, proceed with creating the appointment\n"
                "- Use the create_appointment tool with all the collected SOP information\n"
                "- If any SOP information is missing, inform the user that SOPs need to be completed first\n"
                "- If the user wants to check availability, use the check_availability tool\n"
                "- If the user wants to reschedule, use the reschedule_appointment tool\n"
                "- Be professional and confirm the appointment details after creation\n"
                "- Provide the appointment ID and next steps to the user\n\n"
                "Respond in a helpful, professional manner that builds upon the conversation context."
            ),
            name="appointment_booking_agent"
        )
        
        # Generate response
        response = agent.invoke(state)
        
        logger.info("✅ Appointment Booking agent completed")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in Appointment Booking agent: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
