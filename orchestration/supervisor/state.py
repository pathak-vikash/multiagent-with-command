"""
State management for the supervisor sub-graph.

This module defines the state structure and utilities
for managing supervisor routing and handoff state.
"""

from langgraph.graph import MessagesState
from typing import Dict, Any, Optional
from core.logger import logger

class State(MessagesState):
    """
    Extended state class for supervisor sub-graph.
    
    Includes supervisor routing and handoff state management.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.routing_data: Dict[str, Any] = {}
        self.handoff_data: Dict[str, Any] = {}
        self.workflow_step: str = "initial"
    
    def set_routing_data(self, key: str, value: Any) -> None:
        """Set routing-specific data."""
        self.routing_data[key] = value
        logger.debug(f"Set routing data: {key} = {value}")
    
    def get_routing_data(self, key: str, default: Any = None) -> Any:
        """Get routing-specific data."""
        return self.routing_data.get(key, default)
    
    def set_handoff_data(self, key: str, value: Any) -> None:
        """Set handoff-specific data."""
        self.handoff_data[key] = value
        logger.debug(f"Set handoff data: {key} = {value}")
    
    def get_handoff_data(self, key: str, default: Any = None) -> Any:
        """Get handoff-specific data."""
        return self.handoff_data.get(key, default)
    
    def set_workflow_step(self, step: str) -> None:
        """Set the current workflow step."""
        self.workflow_step = step
        logger.debug(f"Set workflow step: {step}")
    
    def get_workflow_step(self) -> str:
        """Get the current workflow step."""
        return self.workflow_step
    
    def clear_routing_data(self) -> None:
        """Clear all routing data."""
        self.routing_data.clear()
        logger.debug("Cleared all routing data")
    
    def clear_handoff_data(self) -> None:
        """Clear all handoff data."""
        self.handoff_data.clear()
        logger.debug("Cleared all handoff data")

def create() -> State:
    """Create a new supervisor state instance."""
    return State()
