"""
Appointment Sub-Graph - Coordinates SOP collection and appointment booking.
"""

from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt.tool_node import ToolNode
from .state import AppointmentState
from .nodes import sop_collector, booking_agent, start, skip_sop_collector
from tools.appointment_tools import create_appointment, check_availability, reschedule_appointment
from core.logger import logger

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
        
        return "continue"
        
    except Exception as e:
        logger.error(f"Error in should_continue: {str(e)}")
        return "end"


#
# Should Book Appointment
#
def should_book_appointment(state):
    
    # if sop enforcement is complete, then book appointment.
    if state.get("should_route", False):
        return "booking_agent"
    else:
        return "end"

#
# Should Enforce SOP
#
def should_enforce_sop(state):
    # if laready completed the sop enforcement, then skip it.
    should_route = state.get("should_route", False)
    
    if should_route:
        return "skip_sop_collector"
    else:
        return "sop_collector"

def create():
    """Create the appointment sub-graph"""
    try:
        workflow = StateGraph(AppointmentState)
        
        # Add nodes
        workflow.add_node("start", start)
        workflow.add_node("sop_collector", sop_collector)
        workflow.add_node("skip_sop_collector", skip_sop_collector)
        workflow.add_node("booking_agent", booking_agent)
        
        # Use ToolNode for proper tool execution
        booking_tools_node = ToolNode([create_appointment, check_availability, reschedule_appointment])
        workflow.add_node("booking_tools", booking_tools_node)
        
        # Add entry point
        workflow.add_edge(START, "start")

        # required sop enforcement?
        workflow.add_conditional_edges(
            "start",
            should_enforce_sop,
            {
                "sop_collector": "sop_collector",
                "skip_sop_collector": "skip_sop_collector",
            },
        )
        
        # should book appointment?
        workflow.add_conditional_edges(
            "sop_collector",
            should_book_appointment,
            {
                "booking_agent": "booking_agent",
                "end": END,
            },
        )

        # book appointment > continue?
        workflow.add_conditional_edges(
            "booking_agent",
            should_continue,
            {
                "continue": "booking_tools",
                "end": END,
            },
        )

        
        workflow.add_conditional_edges(
            "booking_tools",
            should_continue,
            {
                "continue": "booking_tools",
                "end": END,
            },
        )

        workflow.add_edge("skip_sop_collector", "booking_agent")
        
        return workflow.compile()
        
    except Exception as e:
        logger.error(f"Error creating appointment graph: {str(e)}")
        raise

the_graph = None

def get(args=None):
    global the_graph
    if the_graph is None:
        the_graph = create()
    return the_graph

# Visualize graph
if __name__ == "__main__":
    from utils.graph_visualizer import visualize_graph
    
    graph = get()
    visualize_graph(graph, "Appointment Sub-Graph", include_mermaid=True, include_config=True)
