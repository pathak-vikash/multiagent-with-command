"""
State management for the general agent sub-graph.

This module defines the state structure and utilities
for managing general conversation state.
"""

from langgraph.graph import MessagesState
from typing import Dict, Any, Optional
from core.logger import logger

class State(MessagesState):
    """
    Extended state class for general agent sub-graph.
    
    Includes general conversation state management.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversation_data: Dict[str, Any] = {}
        self.workflow_step: str = "initial"
    
    def set_conversation_data(self, key: str, value: Any) -> None:
        """Set conversation-specific data."""
        self.conversation_data[key] = value
        logger.debug(f"Set conversation data: {key} = {value}")
    
    def get_conversation_data(self, key: str, default: Any = None) -> Any:
        """Get conversation-specific data."""
        return self.conversation_data.get(key, default)
    
    def set_workflow_step(self, step: str) -> None:
        """Set the current workflow step."""
        self.workflow_step = step
        logger.debug(f"Set workflow step: {step}")
    
    def get_workflow_step(self) -> str:
        """Get the current workflow step."""
        return self.workflow_step
    
    def clear_conversation_data(self) -> None:
        """Clear all conversation data."""
        self.conversation_data.clear()
        logger.debug("Cleared all conversation data")

def create() -> State:
    """Create a new general agent state instance."""
    return State()
