import traceback
import re
from datetime import datetime
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode
from tools.appointment_tools import create_appointment, check_availability, reschedule_appointment
from utils import load_template, to_plain_dict
from utils.llm_helpers import create_llm_client
from utils.conversation_formatter import format_recent_conversation
from core.logger import logger
from .state import AppointmentState
from .response_format import SOPExecutionResult

def sop_collector(state) -> AppointmentState:
    try:
        if not state["messages"]:
            return state
            
        last_message = state["messages"][-1]
        task_description = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        conversation_context = format_recent_conversation(state["messages"], exclude_last=1)
        
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
        
        # Return complete state with messages integrated
        updated_state = {
            **state,  # Keep all existing state
            "sop_steps": sop_steps,
            "adherence_percentage": result.adherence_percentage,
            "should_route": result.should_route,
        }
        
        # Add the AI response to messages
        if to_response:
            updated_state["messages"].append(AIMessage(content=to_response))
        
        return updated_state
        
    except Exception as e:
        logger.error(f"Error in SOP Collector agent: {str(e)}")
        raise

def should_enforce_sop(state) -> Literal["sop_collector", "booking_agent"]:
    """Determine if SOP enforcement should continue or move to booking"""
    try:
        # Check if SOP enforcement is complete
        should_route = state.get("should_route", False)
        adherence_percentage = state.get("adherence_percentage", 0.0)
        
        # If SOP is complete (should_route=True) or adherence is 100%, move to booking
        if should_route or adherence_percentage >= 100.0:
            return "booking_agent"
        else:
            return "sop_collector"
            
    except Exception as e:
        logger.error(f"Error in should_enforce_sop: {str(e)}")
        return "sop_collector"

def booking_agent(state) -> AppointmentState:
    """Agent node following official LangGraph pattern"""
    try:
        if not state["messages"]:
            return state
            
        # Extract context from state
        last_message = state["messages"][-1]
        task_description = last_message.content if hasattr(last_message, 'content') else str(last_message)
        sop_steps = state.get("sop_steps", {})
        today = datetime.now().strftime("%Y-%m-%d")
        
        logger.info(f"Booking agent processing: {task_description}")
        
        # Check if this is a tool response and increment retry counter
        current_retry = state.get("retry_count", 0)
        if hasattr(last_message, 'tool_call_id') and last_message.tool_call_id:
            current_retry += 1
            logger.info(f"Retry count: {current_retry}")
        
        # Update state with retry count
        state["retry_count"] = current_retry
        
        # Load and process template with variables
        template_content = load_template("appointment")
        
        # Format SOP steps for template
        sop_steps_formatted = ""
        if sop_steps:
            for step_name, step_data in sop_steps.items():
                status = step_data.get('status', 'unknown')
                value = step_data.get('value', '')
                sop_steps_formatted += f"- {step_name}: {status} (value: {value})\n"
        
        try:
            processed_template = template_content.format(
                today=today,  # Only send today for date reference
                last_message=task_description,
                sop_steps=sop_steps_formatted
            )
        except KeyError as e:
            logger.warning(f"Template variable not found: {e}, using raw template")
            processed_template = template_content
        except Exception as e:
            logger.error(f"Error processing template: {e}")
            processed_template = template_content
        
        # Create LLM with tools - following reference pattern exactly
        llm = create_llm_client()
        tools = [create_appointment, check_availability, reschedule_appointment]
        llm_with_tools = llm.bind_tools(tools)
        
        # Following reference pattern: use ChatPromptTemplate with SystemMessagePromptTemplate
        from langchain_core.prompts import SystemMessagePromptTemplate
        
        messages = [SystemMessagePromptTemplate.from_template(processed_template)]
        prompt = ChatPromptTemplate.from_messages(messages)
        
        # Create formatted messages using the template (following reference pattern)
        context_vars = {
            "today": today,
            "last_message": task_description,
            "sop_steps": sop_steps_formatted
        }
        
        formatted_messages = prompt.format_messages(**context_vars)
        formatted_messages = formatted_messages + state["messages"]
        
        # Invoke with formatted messages (following reference pattern)
        response = llm_with_tools.invoke(formatted_messages)
        
        # Create proper AIMessage with additional_kwargs (following reference pattern)
        from langchain_core.messages import AIMessage
        output = AIMessage(
            content=response.content, 
            additional_kwargs=response.additional_kwargs
        )
        
        # Log tool calls if present
        if hasattr(output, 'additional_kwargs') and 'tool_calls' in output.additional_kwargs:
            tool_calls = output.additional_kwargs.get('tool_calls', [])
            if tool_calls:
                logger.info(f"Tool calls detected: {len(tool_calls)}")
                # Update processed tool calls to track usage
                current_processed = state.get("processed_tool_calls", set())
                tool_call_ids = {tc.get("id") for tc in tool_calls if tc.get("id")}
                current_processed.update(tool_call_ids)
                state["processed_tool_calls"] = current_processed
        
        # Return state with new message - following reference pattern
        return {
            **state,  # Keep all existing state
            "retry_count": current_retry,  # Update retry count
            "messages": [output]  # Add only the new response message
        }
        
    except Exception as e:
        logger.error(f"Error in Appointment Booking agent: {str(e)}")
        raise

def should_continue(state: AppointmentState) -> Literal["booking_tools", "end"]:
    """Routing function following reference implementation pattern with proper tool call tracking"""
    try:
        messages = state.get("messages", [])
        if not messages:
            return "end"
            
        last_message = messages[-1]
        
        # Check retry counter to prevent infinite loops
        retry_count = state.get("retry_count", 0)
        if retry_count >= 3:
            logger.warning(f"Maximum retry count ({retry_count}) reached, ending workflow")
            return "end"
        
        # Check if there are pending tool calls (following reference pattern)
        if not hasattr(last_message, 'additional_kwargs') or "tool_calls" not in last_message.additional_kwargs:
            return "end"
        
        # Check if tool calls have been processed (following reference pattern)
        processed_tool_calls = state.get("processed_tool_calls", set())
        current_tool_calls = last_message.additional_kwargs.get("tool_calls", [])
        current_tool_call_ids = {tc.get("id") for tc in current_tool_calls if tc.get("id")}
        
        if current_tool_call_ids.issubset(processed_tool_calls):
            return "end"
        
        # Check if the last message is a tool response with an error
        if hasattr(last_message, 'tool_call_id') and last_message.tool_call_id:
            content = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            # Check if tool response indicates an error (starts with "Error:")
            if content.strip().startswith("Error:"):
                logger.warning(f"Tool error detected: {content}")
                return "end"
        
        return "booking_tools"
        
    except Exception as e:
        logger.error(f"Error in should_continue: {str(e)}")
        return "end"
