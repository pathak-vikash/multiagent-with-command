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
    workflow = StateGraph(State)
    
    workflow.add_node("advisor_agent", advisor_agent)
    
    workflow.add_edge(START, "advisor_agent")
    
    workflow.add_edge("advisor_agent", END)
    
    return workflow.compile()

def node(state) -> State:
    try:
        logger.info("Starting advisor agent sub-graph workflow")
        
        sub_graph = create()
        result = sub_graph.invoke(state)
        
        logger.info("Advisor agent sub-graph workflow completed")
        return result
        
    except Exception as e:
        logger.error(f"Error in advisor agent sub-graph: {str(e)}")
        raise

_advisor_subgraph = None

def get():
    global _advisor_subgraph
    if _advisor_subgraph is None:
        _advisor_subgraph = create()
    return _advisor_subgraph
