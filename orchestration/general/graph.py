"""
General Agent Sub-Graph - Handles general conversation and greetings.

This sub-graph manages general conversation workflow.
"""

import traceback
from langgraph.graph import StateGraph, START, END
from .state import State
from .nodes import general_agent
from core.logger import logger

def create():
    """
    Create the general agent sub-graph.
    
    Returns:
        CompiledStateGraph: The compiled general agent sub-graph
    """
    
    # Create the workflow with State
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("general_agent", general_agent)
    
    # Add entry point
    workflow.add_edge(START, "general_agent")
    
    # General agent ends the conversation
    workflow.add_edge("general_agent", END)
    
    return workflow.compile()

def node(state) -> State:
    """
    Main entry point for the general agent sub-graph.
    
    This function invokes the general conversation workflow
    and returns the final result.
    """
    
    try:
        logger.info("🚀 Starting general agent sub-graph workflow")
        
        # Create and invoke the sub-graph
        sub_graph = create()
        result = sub_graph.invoke(state)
        
        logger.info("✅ General agent sub-graph workflow completed")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error in general agent sub-graph: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

# Create a singleton instance for reuse
_general_subgraph = None

def get():
    """
    Get a singleton instance of the general agent sub-graph.
    
    Returns:
        CompiledStateGraph: The compiled general agent sub-graph
    """
    global _general_subgraph
    if _general_subgraph is None:
        _general_subgraph = create()
    return _general_subgraph
