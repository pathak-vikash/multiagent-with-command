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
    workflow = StateGraph(State)
    
    workflow.add_node("estimate_agent", estimate_agent)
    
    workflow.add_edge(START, "estimate_agent")
    workflow.add_edge("estimate_agent", END)
    
    return workflow.compile()

def node(state) -> State:
    try:
        logger.info("Starting estimate agent sub-graph workflow")
        
        sub_graph = create()
        result = sub_graph.invoke(state)
        
        logger.info("Estimate agent sub-graph workflow completed")
        return result
        
    except Exception as e:
        logger.error(f"Error in estimate agent sub-graph: {str(e)}")
        raise

_estimate_subgraph = None

def get():
    global _estimate_subgraph
    if _estimate_subgraph is None:
        _estimate_subgraph = create()
    return _estimate_subgraph
