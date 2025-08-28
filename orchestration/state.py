"""
Base state management for the main orchestration level.

This module defines the base state structure and utilities
for managing conversation state across the entire system.
"""

from langgraph.graph import MessagesState
from typing import Dict, Any, Optional
from core.logger import logger

class State(MessagesState):
    """
    Extended state class for main orchestration level.
    
    This can be extended to include additional state management
    for the main graph level if needed in the future.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metadata: Dict[str, Any] = {}
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the state."""
        self.metadata[key] = value
        logger.debug(f"Added metadata: {key} = {value}")
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata from the state."""
        return self.metadata.get(key, default)
    
    def clear_metadata(self) -> None:
        """Clear all metadata."""
        self.metadata.clear()
        logger.debug("Cleared all metadata")

def create() -> State:
    """Create a new orchestration state instance."""
    return State()
