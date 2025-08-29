"""
Central nodes reference for all orchestration agents.

This module provides a centralized reference to all agent nodes
from the various sub-graphs with proper state management.
"""

from typing import Dict, Any
from core.logger import logger
from langgraph.types import Command
from .state import State
from .schema import Node

# Import all agent nodes from sub-graphs
from .general.nodes import general_agent as general
from .appointment.graph import get as appointment_graph
from .support.nodes import support_agent as support_agent_func
from .estimate.nodes import estimate_agent as estimate_agent_func
from .advisor.nodes import advisor_agent as advisor_agent_func


def start(state: State) -> State:
    """Start agent node."""
    try:
        # Get the current value from the state and use command to route to that node
        current_agent = state.get("current", Node.APPOINTMENT.value)
        
        logger.info(f"Start node routing to: {current_agent}")
        
        # Return command to route to the appropriate agent
        return Command(goto=current_agent)
        
    except Exception as e:
        logger.error(f"Error in start node: {str(e)}")
        # Fallback to appointment agent
        return Command(goto=Node.APPOINTMENT.value)

def appointment(state: State) -> State:
    """Appointment agent node."""
    try:
        logger.info("Starting appointment sub-graph workflow")
        
        # Invoke appointment sub-graph with current state
        sub_graph = appointment_graph()
        result = sub_graph.invoke(state)
        
        logger.info("Appointment sub-graph completed successfully")

        logger.info(f"Appointment sub-graph result: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in appointment sub-graph: {str(e)}")
        raise

def support(state: State) -> State:
    """Support agent node."""
    try:
        logger.info("Starting support sub-graph workflow")
        
        # Invoke support sub-graph with current state
        result = support_agent_func(state)
        
        logger.info("Support sub-graph completed successfully")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in support sub-graph: {str(e)}")
        raise

def estimate(state: State) -> State:
    """Estimate agent node."""
    try:
        logger.info("Starting estimate sub-graph workflow")
        
        # Invoke estimate sub-graph with current state
        result = estimate_agent_func(state)
        
        logger.info("Estimate sub-graph completed successfully")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in estimate sub-graph: {str(e)}")
        raise

def advisor(state: State) -> State:
    """Advisor agent node."""
    try:
        logger.info("Starting advisor sub-graph workflow")
        
        # Invoke advisor sub-graph with current state
        result = advisor_agent_func(state)
        
        logger.info("Advisor sub-graph completed successfully")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in advisor sub-graph: {str(e)}")
        raise

# Export all nodes with proper state management
__all__ = [
    'start',
    'general',
    'appointment',
    'support', 
    'estimate',
    'advisor'
]
