"""
Advisor Agent Sub-Graph - Handles business information and recommendations.

This sub-graph manages advisor workflow.
"""

import traceback
from langgraph.graph import StateGraph, START, END
from .state import State
from .nodes import advisor_agent
from core.logger import logger

def create():
    """
    Create the advisor agent sub-graph.
    
    Returns:
        CompiledStateGraph: The compiled advisor agent sub-graph
    """
    
    # Create the workflow with State
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("advisor_agent", advisor_agent)
    
    # Add entry point
    workflow.add_edge(START, "advisor_agent")
    
    # Advisor agent ends the conversation
    workflow.add_edge("advisor_agent", END)
    
    return workflow.compile()

def node(state) -> State:
    """
    Main entry point for the advisor agent sub-graph.
    
    This function invokes the advisor workflow
    and returns the final result.
    """
    
    try:
        logger.info("🚀 Starting advisor agent sub-graph workflow")
        
        # Create and invoke the sub-graph
        sub_graph = create()
        result = sub_graph.invoke(state)
        
        logger.info("✅ Advisor agent sub-graph workflow completed")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error in advisor agent sub-graph: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

# Create a singleton instance for reuse
_advisor_subgraph = None

def get():
    """
    Get a singleton instance of the advisor agent sub-graph.
    
    Returns:
        CompiledStateGraph: The compiled advisor agent sub-graph
    """
    global _advisor_subgraph
    if _advisor_subgraph is None:
        _advisor_subgraph = create()
    return _advisor_subgraph
