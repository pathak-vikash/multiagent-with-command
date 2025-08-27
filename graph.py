"""
LangGraph Multi-Agent Supervisor Graph Composition

This module contains the centralized graph composition logic following the official
LangGraph supervisor pattern from supervisor-tools.py.
"""

from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from agents.supervisor import supervisor_node
from agents.general_agent import general_agent_node
from agents.appointment_agent import appointment_agent_node
from agents.support_agent import support_agent_node
from agents.estimate_agent import estimate_agent_node
from agents.advisor_agent import advisor_agent_node

def create_supervisor_graph():
    """
    Create the complete supervisor graph with all agents following the official pattern.
    
    This follows the exact pattern from the LangGraph supervisor-tools.py example:
    - A supervisor node that uses handoff tools to transfer requests
    - Specialized agent nodes for different business domains
    - Agents end the conversation after processing (no infinite loops)
    - Uses MessagesState for proper message handling
    
    Returns:
        CompiledStateGraph: The compiled LangGraph workflow
    """
    
    # Create the workflow with MessagesState (following official pattern)
    workflow = StateGraph(MessagesState)
    
    # Add all nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("general_agent", general_agent_node)
    workflow.add_node("appointment_agent", appointment_agent_node)
    workflow.add_node("support_agent", support_agent_node)
    workflow.add_node("estimate_agent", estimate_agent_node)
    workflow.add_node("advisor_agent", advisor_agent_node)
    
    # Add entry point
    workflow.add_edge(START, "supervisor")
    
    # Agents end the conversation after processing (prevent infinite loops)
    workflow.add_edge("general_agent", END)
    workflow.add_edge("appointment_agent", END)
    workflow.add_edge("support_agent", END)
    workflow.add_edge("estimate_agent", END)
    workflow.add_edge("advisor_agent", END)
    
    return workflow.compile()

def get_graph_info():
    """
    Get information about the graph structure for documentation and debugging.
    
    Returns:
        dict: Information about the graph nodes and edges
    """
    return {
        "nodes": [
            "supervisor",
            "general_agent", 
            "appointment_agent",
            "support_agent",
            "estimate_agent",
            "advisor_agent"
        ],
        "entry_point": "supervisor",
        "agent_types": {
            "general_agent": "Casual conversation and greetings (LLM agent)",
            "appointment_agent": "Appointment booking and scheduling (LLM agent)",
            "support_agent": "Customer support and warranty claims (LLM agent)",
            "estimate_agent": "Price quotes and estimates (LLM agent)",
            "advisor_agent": "Business information and recommendations (LLM agent)"
        },
        "state_type": "MessagesState (official LangGraph pattern)",
        "routing_method": "Supervisor with handoff tools using Command/Send pattern",
        "features": [
            "Supervisor with handoff tools",
            "Task description handoffs",
            "Agent-to-agent transfers using Command and Send",
            "Structured responses with Pydantic schemas",
            "Tool integration for business operations",
            "Conversation history tracking"
        ],
        "handoff_mechanism": "Supervisor uses handoff tools to transfer requests with task descriptions"
    }

# Create a singleton instance for reuse
_supervisor_graph = None

def get_supervisor_graph():
    """
    Get a singleton instance of the supervisor graph.
    
    This function ensures that the graph is only created once and reused
    across multiple calls, improving performance.
    
    Returns:
        CompiledStateGraph: The compiled supervisor graph
    """
    global _supervisor_graph
    if _supervisor_graph is None:
        _supervisor_graph = create_supervisor_graph()
    return _supervisor_graph

def reset_graph():
    """
    Reset the singleton graph instance.
    
    This is useful for testing or when you need to recreate the graph
    with different configurations.
    """
    global _supervisor_graph
    _supervisor_graph = None
