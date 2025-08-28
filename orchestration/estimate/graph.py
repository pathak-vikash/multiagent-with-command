"""
Estimate Agent Sub-Graph - Handles price quotes and estimates.

This sub-graph manages estimate workflow.
"""

import traceback
from langgraph.graph import StateGraph, START, END
from .state import State
from .nodes import estimate_agent
from core.logger import logger

def create():
    """
    Create the estimate agent sub-graph.
    
    Returns:
        CompiledStateGraph: The compiled estimate agent sub-graph
    """
    
    # Create the workflow with State
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("estimate_agent", estimate_agent)
    
    # Add entry point
    workflow.add_edge(START, "estimate_agent")
    
    # Estimate agent ends the conversation
    workflow.add_edge("estimate_agent", END)
    
    return workflow.compile()

def node(state) -> State:
    """
    Main entry point for the estimate agent sub-graph.
    
    This function invokes the estimate workflow
    and returns the final result.
    """
    
    try:
        logger.info("🚀 Starting estimate agent sub-graph workflow")
        
        # Create and invoke the sub-graph
        sub_graph = create()
        result = sub_graph.invoke(state)
        
        logger.info("✅ Estimate agent sub-graph workflow completed")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error in estimate agent sub-graph: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

# Create a singleton instance for reuse
_estimate_subgraph = None

def get():
    """
    Get a singleton instance of the estimate agent sub-graph.
    
    Returns:
        CompiledStateGraph: The compiled estimate agent sub-graph
    """
    global _estimate_subgraph
    if _estimate_subgraph is None:
        _estimate_subgraph = create()
    return _estimate_subgraph
