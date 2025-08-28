"""
Support Agent Sub-Graph - Handles support tickets and warranty claims.

This sub-graph manages support workflow.
"""

import traceback
from langgraph.graph import StateGraph, START, END
from .state import State
from .nodes import support_agent
from core.logger import logger

def create():
    """
    Create the support agent sub-graph.
    
    Returns:
        CompiledStateGraph: The compiled support agent sub-graph
    """
    
    # Create the workflow with State
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("support_agent", support_agent)
    
    # Add entry point
    workflow.add_edge(START, "support_agent")
    
    # Support agent ends the conversation
    workflow.add_edge("support_agent", END)
    
    return workflow.compile()

def node(state) -> State:
    """
    Main entry point for the support agent sub-graph.
    
    This function invokes the support workflow
    and returns the final result.
    """
    
    try:
        logger.info("🚀 Starting support agent sub-graph workflow")
        
        # Create and invoke the sub-graph
        sub_graph = create()
        result = sub_graph.invoke(state)
        
        logger.info("✅ Support agent sub-graph workflow completed")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error in support agent sub-graph: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

# Create a singleton instance for reuse
_support_subgraph = None

def get():
    """
    Get a singleton instance of the support agent sub-graph.
    
    Returns:
        CompiledStateGraph: The compiled support agent sub-graph
    """
    global _support_subgraph
    if _support_subgraph is None:
        _support_subgraph = create()
    return _support_subgraph
