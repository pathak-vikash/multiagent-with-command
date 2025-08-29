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
    workflow = StateGraph(State)
    
    workflow.add_node("general_agent", general_agent)
    
    workflow.add_edge(START, "general_agent")
    workflow.add_edge("general_agent", END)
    
    return workflow.compile()

def node(state) -> State:
    try:
        logger.info("Starting general agent sub-graph workflow")
        
        sub_graph = create()
        result = sub_graph.invoke(state)
        
        logger.info("General agent sub-graph workflow completed")
        return result
        
    except Exception as e:
        logger.error(f"Error in general agent sub-graph: {str(e)}")
        raise

_general_subgraph = None

def get():
    global _general_subgraph
    if _general_subgraph is None:
        _general_subgraph = create()
    return _general_subgraph
