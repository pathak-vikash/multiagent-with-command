"""
State management for the support agent sub-graph.

This module defines the state structure and utilities
for managing support ticket and warranty claim state.
"""

from langgraph.graph import MessagesState
from typing import Dict, Any, Optional
from core.logger import logger

class State(MessagesState):
    """
    Extended state class for support agent sub-graph.
    
    Includes support ticket and warranty claim state management.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.support_data: Dict[str, Any] = {}
        self.ticket_data: Dict[str, Any] = {}
        self.workflow_step: str = "initial"
    
    def set_support_data(self, key: str, value: Any) -> None:
        """Set support-specific data."""
        self.support_data[key] = value
        logger.debug(f"Set support data: {key} = {value}")
    
    def get_support_data(self, key: str, default: Any = None) -> Any:
        """Get support-specific data."""
        return self.support_data.get(key, default)
    
    def set_ticket_data(self, key: str, value: Any) -> None:
        """Set ticket-specific data."""
        self.ticket_data[key] = value
        logger.debug(f"Set ticket data: {key} = {value}")
    
    def get_ticket_data(self, key: str, default: Any = None) -> Any:
        """Get ticket-specific data."""
        return self.ticket_data.get(key, default)
    
    def set_workflow_step(self, step: str) -> None:
        """Set the current workflow step."""
        self.workflow_step = step
        logger.debug(f"Set workflow step: {step}")
    
    def get_workflow_step(self) -> str:
        """Get the current workflow step."""
        return self.workflow_step
    
    def clear_support_data(self) -> None:
        """Clear all support data."""
        self.support_data.clear()
        logger.debug("Cleared all support data")
    
    def clear_ticket_data(self) -> None:
        """Clear all ticket data."""
        self.ticket_data.clear()
        logger.debug("Cleared all ticket data")

def create() -> State:
    """Create a new support agent state instance."""
    return State()
