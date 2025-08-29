"""
Supervisor Sub-Graph - Handles routing and handoff management.

This sub-graph manages supervisor workflow.
"""

import traceback
from langgraph.graph import StateGraph, START, END
from orchestration.state import State
from orchestration.schema import Node
from .nodes import supervisor
from core.logger import logger

def create():
    workflow = StateGraph(State)
    
    workflow.add_node(Node.SUPERVISOR.value, supervisor)
    workflow.add_edge(START, Node.SUPERVISOR.value)
    workflow.add_edge(Node.SUPERVISOR.value, END)
    
    return workflow.compile()

def node(state) -> State:
    try:
        logger.info("Starting supervisor sub-graph workflow")
        
        sub_graph = create()
        result = sub_graph.invoke(state)
        
        logger.info("Supervisor sub-graph workflow completed")
        return result
        
    except Exception as e:
        logger.error(f"Error in supervisor sub-graph: {str(e)}")
        raise

_supervisor_subgraph = None

def get():
    global _supervisor_subgraph
    if _supervisor_subgraph is None:
        _supervisor_subgraph = create()
    return _supervisor_subgraph
