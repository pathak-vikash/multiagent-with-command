"""
Supervisor Sub-Graph - Handles routing and handoff management.

This sub-graph manages supervisor workflow.
"""

import traceback
from langgraph.graph import StateGraph, START, END
from .state import State
from .nodes import supervisor
from core.logger import logger

def create():
    """
    Create the supervisor sub-graph.
    
    Returns:
        CompiledStateGraph: The compiled supervisor sub-graph
    """
    
    # Create the workflow with State
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor)
    
    # Add entry point
    workflow.add_edge(START, "supervisor")
    
    # Supervisor ends the conversation (handoff handled by ParentCommand)
    workflow.add_edge("supervisor", END)
    
    return workflow.compile()

def node(state) -> State:
    """
    Main entry point for the supervisor sub-graph.
    
    This function invokes the supervisor workflow
    and returns the final result.
    """
    
    try:
        logger.info("🚀 Starting supervisor sub-graph workflow")
        
        # Create and invoke the sub-graph
        sub_graph = create()
        result = sub_graph.invoke(state)
        
        logger.info("✅ Supervisor sub-graph workflow completed")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error in supervisor sub-graph: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

# Create a singleton instance for reuse
_supervisor_subgraph = None

def get():
    """
    Get a singleton instance of the supervisor sub-graph.
    
    Returns:
        CompiledStateGraph: The compiled supervisor sub-graph
    """
    global _supervisor_subgraph
    if _supervisor_subgraph is None:
        _supervisor_subgraph = create()
    return _supervisor_subgraph
