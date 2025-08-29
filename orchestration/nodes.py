"""
Central nodes reference for all orchestration agents.

This module provides a centralized reference to all agent nodes
from the various sub-graphs with proper state management.
"""

from typing import Dict, Any, List
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


def filter_tool_messages(messages: List) -> List:
    """
    Filter out tool messages to prevent OpenAI API errors.
    Tool messages require proper tool_calls context which may not be available.
    
    Args:
        messages: List of messages to filter
        
    Returns:
        List of messages with tool messages removed
    """
    filtered_messages = []
    for message in messages:
        # Check for tool messages in multiple ways
        is_tool_message = (
            hasattr(message, 'type') and message.type == 'tool' or
            hasattr(message, '__class__') and 'ToolMessage' in str(message.__class__) or
            hasattr(message, 'role') and message.role == 'tool'
        )
        
        if is_tool_message:
            logger.debug(f"Filtering out tool message: {message}")
            continue
        filtered_messages.append(message)
    
    return filtered_messages


def clean_state_for_agent(state: State) -> State:
    """
    Clean state by filtering out tool messages and ensuring proper structure.
    
    Args:
        state: Original state object
        
    Returns:
        Cleaned state object
    """
    try:
        # Create a copy of the state
        cleaned_state = state.copy()
        
        # Filter out tool messages if messages exist
        if "messages" in cleaned_state and cleaned_state["messages"]:
            cleaned_state["messages"] = filter_tool_messages(cleaned_state["messages"])
            logger.debug(f"Filtered {len(state['messages']) - len(cleaned_state['messages'])} tool messages")
        
        return cleaned_state
        
    except Exception as e:
        logger.error(f"Error cleaning state: {str(e)}")
        # Return original state if cleaning fails
        return state


def start(state: State) -> State:
    """Start agent node."""
    try:
        # Clean the state by filtering out tool messages
        cleaned_state = clean_state_for_agent(state)
        
        # Get the current value from the state and use command to route to that node
        current_agent = cleaned_state.get("current", Node.APPOINTMENT.value)
        
        logger.info(f"Start node routing to: {current_agent}")
        logger.debug(f"State cleaned: {len(state.get('messages', []))} -> {len(cleaned_state.get('messages', []))} messages")
        
        # Update the state with cleaned messages
        state.update(cleaned_state)
        
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
        
        # State is already cleaned by start node
        sub_graph = appointment_graph()
        result = sub_graph.invoke(state)
        
        logger.info("Appointment sub-graph completed successfully")
        logger.info(f"Appointment sub-graph result: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in appointment sub-graph: {str(e)}")
        return {
            "current": state.get("current", "appointment")
        }

def support(state: State) -> State:
    """Support agent node."""
    try:
        logger.info("Starting support sub-graph workflow")
        
        # State is already cleaned by start node
        result = support_agent_func(state)
        
        logger.info("Support sub-graph completed successfully")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in support sub-graph: {str(e)}")
        return {
            "current": state.get("current", "support")
        }

def estimate(state: State) -> State:
    """Estimate agent node."""
    try:
        logger.info("Starting estimate sub-graph workflow")
        
        # State is already cleaned by start node
        result = estimate_agent_func(state)
        
        logger.info("Estimate sub-graph completed successfully")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in estimate sub-graph: {str(e)}")
        return {
            "current": state.get("current", "estimate")
        }

def advisor(state: State) -> State:
    """Advisor agent node."""
    try:
        logger.info("Starting advisor sub-graph workflow")
        
        # State is already cleaned by start node
        result = advisor_agent_func(state)
        
        logger.info("Advisor sub-graph completed successfully")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in advisor sub-graph: {str(e)}")
        return {
            "current": state.get("current", "advisor")
        }

# Export all nodes with proper state management
__all__ = [
    'start',
    'general',
    'appointment',
    'support', 
    'estimate',
    'advisor'
]
