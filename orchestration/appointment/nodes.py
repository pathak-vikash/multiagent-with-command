import traceback
import re
from datetime import datetime
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate
from langchain_core.messages import AIMessage
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode
from tools.appointment_tools import create_appointment, check_availability, reschedule_appointment
from utils import load_template, to_plain_dict, to_plain_text
from utils.llm_helpers import create_llm_client
from utils.helper import format_conversation_history
from core.logger import logger
from .state import AppointmentState
from .response_format import SOPExecutionResult


#
# Start
#
def start(state) -> AppointmentState:
    return {
        "messages": []
    }

def skip_sop_collector(state):
        
    # use existing state.
    response = {
        "sop_steps": state.get("sop_steps", {}),
        "adherence_percentage": state.get("adherence_percentage", 0),
        "should_route": state.get("should_route", False)
    }
    
    return response

def sop_collector(state) -> AppointmentState:
    try:
        if not state["messages"]:
            return state
            
        last_message = state["messages"][-1]
        task_description = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        conversation_context = format_conversation_history(state["messages"])
        
        # Debug conversation context
        logger.info(f"SOP Collector Debug - Conversation context: {conversation_context}")
        logger.info(f"SOP Collector Debug - Messages count: {len(state['messages'])}")
        
        llm = create_llm_client()

        # Get template and context data
        sop_prompt_template = load_template("sop_enforcer")
        sop_checklists = load_template(f"sop_checklists/appointment")

        
        # existing state values.
        previous_sop_state = state.get("sop_steps", [])
            
        # Construct prompt and messages
        inputs = {
            "last_message": task_description,
            "conversation_history": conversation_context,
            "previous_sop_state": previous_sop_state,
            "sop_checklists": sop_checklists
        }

        messages = [("system", sop_prompt_template)]
        sop_prompt = ChatPromptTemplate.from_messages(messages)

        # Execute SOP enforcement chain using updated output (EnforceSop now is updated to SOPExecutionResult)
        sop_chain = sop_prompt | llm.with_structured_output(SOPExecutionResult, method="function_calling")
        result: SOPExecutionResult = sop_chain.invoke(inputs)

        sop_steps = to_plain_dict(result.sop_steps)

        # Filter pending SOP steps that have input mapping
        pending_sop_steps = {
            key: value for key, value in sop_steps.items() 
            if value.get('status') == 'pending'
        }

        to_response = ""

        if len(pending_sop_steps) > 0:
            first_pending_step = next(iter(pending_sop_steps.items()), None)
            to_response = first_pending_step[1].get('question', '')
            logger.info(f"SOP Collector: Asking for {first_pending_step[0]} - {to_response}")
        else:
            logger.info("SOP Collector: No pending steps found")
        

        return {
            "sop_steps": sop_steps,
            "adherence_percentage": result.adherence_percentage,
            "should_route": result.should_route,
            "messages": [AIMessage(content=to_response)]
        }
        
    except Exception as e:
        logger.error(f"Error in SOP Collector agent: {str(e)}")
        return {
            "messages": [SystemMessage(content="Error: " + str(e))]
        }


def booking_agent(state) -> AppointmentState:
    """Agent node following official LangGraph pattern"""
    try:
        
        # Extract context from state
        last_message = state["messages"][-1]
        task_description = last_message.content if hasattr(last_message, 'content') else str(last_message)
        sop_steps = state.get("sop_steps", {})
        today = datetime.now().strftime("%Y-%m-%d")
        
        logger.info(f"Booking agent processing: {task_description}")
        
        # Load and process template with variables
        appointment_template = load_template("appointment")
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(appointment_template)
        ])
        
        # Create formatted messages using the template (following reference pattern)
        context_vars = {
            "today": today,
            "last_message": task_description,
            "sop_steps": to_plain_text(sop_steps)
        }
        
        formatted_messages = prompt.format_messages(**context_vars)
        formatted_messages = formatted_messages + state["messages"]
        
        # Create LLM with tools - following reference pattern exactly
        llm = create_llm_client()
        tools = [create_appointment, check_availability, reschedule_appointment]
        llm_with_tools = llm.bind_tools(tools)

        response = llm_with_tools.invoke(formatted_messages)
        
        # Create proper AIMessage with additional_kwargs (following reference pattern)
        output = AIMessage(
            content=response.content, 
            additional_kwargs=response.additional_kwargs
        )
        
        return {
            "messages": [output]
        }
        
    except Exception as e:
        logger.error(f"Error in Appointment Booking agent: {str(e)}")
        return {
            "messages": [SystemMessage(content="Error: " + str(e))]
        }
