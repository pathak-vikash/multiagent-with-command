"""
Router Sub-Graph - Handles routing and handoff management.

This sub-graph manages router workflow.
"""

import traceback
from langgraph.graph import StateGraph, START, END
from orchestration.state import State
from orchestration.schema import Node
from .nodes import router
from core.logger import logger

def create():
    workflow = StateGraph(State)
    
    workflow.add_node(Node.ROUTER.value, router)
    workflow.add_edge(START, Node.ROUTER.value)
    workflow.add_edge(Node.ROUTER.value, END)
    
    return workflow.compile()

def node(state) -> State:
    try:
        logger.info("Starting router sub-graph workflow")
        
        sub_graph = create()
        result = sub_graph.invoke(state)
        
        logger.info("Router sub-graph workflow completed")
        return result
        
    except Exception as e:
        logger.error(f"Error in router sub-graph: {str(e)}")
        raise

_router_subgraph = None

def get():
    global _router_subgraph
    if _router_subgraph is None:
        _router_subgraph = create()
    return _router_subgraph
