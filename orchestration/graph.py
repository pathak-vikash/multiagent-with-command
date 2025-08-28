"""
Main Orchestration Graph - Central coordinator for all agents and sub-graphs.

This module contains the centralized graph composition logic following the official
LangGraph supervisor pattern. It coordinates the main workflow and routes requests
to appropriate agents and sub-graphs.
"""

from langgraph.graph import StateGraph, START, END
from .state import State
from .supervisor.nodes import supervisor
from .nodes import general, appointment, support, estimate, advisor

def create():
    """
    Create the complete main orchestration graph with all agents and sub-graphs.
    
    This follows the exact pattern from the LangGraph supervisor-tools.py example:
    - A supervisor node that uses handoff tools to transfer requests
    - Specialized agent nodes for different business domains
    - Sub-graphs for complex workflows (like appointment booking)
    - Agents end the conversation after processing (no infinite loops)
    - Uses OrchestrationState for proper message handling
    
    Returns:
        CompiledStateGraph: The compiled LangGraph workflow
    """
    
    # Create the workflow with State
    workflow = StateGraph(State)
    
    # Add all nodes
    workflow.add_node("supervisor", supervisor)
    workflow.add_node("general", general)
    workflow.add_node("appointment", appointment)
    workflow.add_node("support", support)
    workflow.add_node("estimate", estimate)
    workflow.add_node("advisor", advisor)
    
    # Add entry point
    workflow.add_edge(START, "supervisor")
    
    # Agents end the conversation after processing (prevent infinite loops)
    workflow.add_edge("general", END)
    workflow.add_edge("appointment", END)
    workflow.add_edge("support", END)
    workflow.add_edge("estimate", END)
    workflow.add_edge("advisor", END)
    
    return workflow.compile()

def get():
    """
    Get a singleton instance of the main orchestration graph.
    
    This function ensures that the graph is only created once and reused
    across multiple calls, improving performance.
    
    Returns:
        CompiledStateGraph: The compiled main orchestration graph
    """
    global _main_orchestration_graph
    if _main_orchestration_graph is None:
        _main_orchestration_graph = create()
    return _main_orchestration_graph

def get_info():
    """
    Get information about the graph structure for documentation and debugging.
    
    Returns:
        dict: Information about the graph nodes and edges
    """
    return {
        "nodes": [
            "supervisor",
            "general", 
            "appointment",
            "support",
            "estimate",
            "advisor"
        ],
        "entry_point": "supervisor",
        "agent_types": {
            "supervisor": "Supervisor sub-graph (routing and handoff)",
            "general": "General conversation sub-graph",
            "appointment": "Appointment booking sub-graph (SOP Collector + Booking Agent)",
            "support": "Support sub-graph (tickets and warranty claims)",
            "estimate": "Estimate sub-graph (pricing and quotes)",
            "advisor": "Advisor sub-graph (business information and recommendations)"
        },
        "state_type": "State (extended MessagesState)",
        "routing_method": "Supervisor with handoff tools using Command/Send pattern",
        "features": [
            "Supervisor with handoff tools",
            "Task description handoffs",
            "Agent-to-agent transfers using Command and Send",
            "Structured responses with Pydantic schemas",
            "Tool integration for business operations",
            "Conversation history tracking",
            "Appointment sub-graph with SOP collection and booking workflow",
            "State management at orchestration and sub-graph levels"
        ],
        "handoff_mechanism": "Supervisor uses handoff tools to transfer requests with task descriptions",
        "sub_graphs": {
            "supervisor": {
                "description": "Supervisor routing and handoff workflow",
                "nodes": ["supervisor"],
                "state": "State"
            },
            "general": {
                "description": "General conversation workflow",
                "nodes": ["general_agent"],
                "state": "State"
            },
            "appointment": {
                "description": "Appointment booking workflow with SOP collection",
                "nodes": ["sop_collector", "appointment_booking"],
                "state": "AppointmentState"
            },
            "support": {
                "description": "Support ticket and warranty claim workflow",
                "nodes": ["support_agent"],
                "state": "State"
            },
            "estimate": {
                "description": "Estimate and pricing workflow",
                "nodes": ["estimate_agent"],
                "state": "State"
            },
            "advisor": {
                "description": "Business information and recommendations workflow",
                "nodes": ["advisor_agent"],
                "state": "State"
            }
        }
    }

# Create a singleton instance for reuse
_main_orchestration_graph = None

def reset():
    """
    Reset the singleton graph instance.
    
    This is useful for testing or when you need to recreate the graph
    with different configurations.
    """
    global _main_orchestration_graph
    _main_orchestration_graph = None
