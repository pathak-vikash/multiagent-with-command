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
    workflow = StateGraph(State)
    
    workflow.add_node("support_agent", support_agent)
    
    workflow.add_edge(START, "support_agent")
    workflow.add_edge("support_agent", END)
    
    return workflow.compile()

def node(state) -> State:
    try:
        logger.info("Starting support agent sub-graph workflow")
        
        sub_graph = create()
        result = sub_graph.invoke(state)
        
        logger.info("Support agent sub-graph workflow completed")
        return result
        
    except Exception as e:
        logger.error(f"Error in support agent sub-graph: {str(e)}")
        raise

_support_subgraph = None

def get():
    global _support_subgraph
    if _support_subgraph is None:
        _support_subgraph = create()
    return _support_subgraph
