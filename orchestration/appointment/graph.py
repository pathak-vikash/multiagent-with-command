"""
Appointment Sub-Graph - Coordinates SOP collection and appointment booking.

This sub-graph manages the complete appointment booking workflow:
1. SOP Collector Agent - Collects and validates all 5 SOPs
2. Appointment Booking Agent - Handles the actual booking after SOPs are complete
"""

import traceback
from langgraph.graph import StateGraph, START, END
from .state import AppointmentState
from .nodes import sop_collector, booking_agent
from core.logger import logger

def create():
    """
    Create the appointment sub-graph that coordinates SOP collection and booking.
    
    This sub-graph follows a sequential workflow:
    1. SOP Collector Agent collects and validates all 5 SOPs
    2. Appointment Booking Agent handles the actual booking
    
    Returns:
        CompiledStateGraph: The compiled appointment sub-graph
    """
    
    # Create the workflow with AppointmentState
    workflow = StateGraph(AppointmentState)
    
    # Add nodes
    workflow.add_node("sop_collector", sop_collector)
    workflow.add_node("appointment_booking", booking_agent)
    
    # Add entry point
    workflow.add_edge(START, "sop_collector")
    
    # SOP collector proceeds to booking agent
    workflow.add_edge("sop_collector", "appointment_booking")
    
    # Booking agent ends the conversation
    workflow.add_edge("appointment_booking", END)
    
    return workflow.compile()

def node(state) -> AppointmentState:
    """
    Main entry point for the appointment sub-graph.
    
    This function invokes the complete appointment booking workflow
    and returns the final result.
    """
    
    try:
        logger.info("🚀 Starting appointment sub-graph workflow")
        
        # Create and invoke the sub-graph
        sub_graph = create()
        result = sub_graph.invoke(state)
        
        logger.info("✅ Appointment sub-graph workflow completed")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error in appointment sub-graph: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

# Create a singleton instance for reuse
_appointment_subgraph = None

def get():
    """
    Get a singleton instance of the appointment sub-graph.
    
    Returns:
        CompiledStateGraph: The compiled appointment sub-graph
    """
    global _appointment_subgraph
    if _appointment_subgraph is None:
        _appointment_subgraph = create()
    return _appointment_subgraph
