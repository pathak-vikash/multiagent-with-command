"""
Appointment Sub-Graph - Coordinates SOP collection and appointment booking.
"""

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt.tool_node import ToolNode
from .state import AppointmentState
from .nodes import sop_collector, booking_agent, should_continue, should_enforce_sop
from tools.appointment_tools import create_appointment, check_availability, reschedule_appointment
from core.logger import logger

def create():
    """Create the appointment sub-graph"""
    try:
        workflow = StateGraph(AppointmentState)
        
        # Add nodes
        workflow.add_node("sop_collector", sop_collector)
        workflow.add_node("booking_agent", booking_agent)
        
        # Use ToolNode for proper tool execution
        booking_tools_node = ToolNode([create_appointment, check_availability, reschedule_appointment])
        workflow.add_node("booking_tools", booking_tools_node)
        
        # Add entry point
        workflow.add_edge(START, "sop_collector")
        
        # Add conditional edges
        workflow.add_conditional_edges("sop_collector", should_enforce_sop, {
            "sop_collector": "sop_collector",
            "booking_agent": "booking_agent"
        })
        
        # Add booking agent to tools loop
        workflow.add_conditional_edges("booking_agent", should_continue, {
            "booking_tools": "booking_tools",
            "end": END
        })
        
        # Add tools back to booking agent
        workflow.add_edge("booking_tools", "booking_agent")
        
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
