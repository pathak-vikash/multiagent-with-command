"""
State management for the advisor agent sub-graph.

This module defines the state structure and utilities
for managing business information and recommendations state.
"""

from langgraph.graph import MessagesState
from typing import Dict, Any, Optional
from core.logger import logger

class State(MessagesState):
    """
    Extended state class for advisor agent sub-graph.
    
    Includes business information and recommendations state management.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business_data: Dict[str, Any] = {}
        self.recommendation_data: Dict[str, Any] = {}
        self.workflow_step: str = "initial"
    
    def set_business_data(self, key: str, value: Any) -> None:
        """Set business-specific data."""
        self.business_data[key] = value
        logger.debug(f"Set business data: {key} = {value}")
    
    def get_business_data(self, key: str, default: Any = None) -> Any:
        """Get business-specific data."""
        return self.business_data.get(key, default)
    
    def set_recommendation_data(self, key: str, value: Any) -> None:
        """Set recommendation-specific data."""
        self.recommendation_data[key] = value
        logger.debug(f"Set recommendation data: {key} = {value}")
    
    def get_recommendation_data(self, key: str, default: Any = None) -> Any:
        """Get recommendation-specific data."""
        return self.recommendation_data.get(key, default)
    
    def set_workflow_step(self, step: str) -> None:
        """Set the current workflow step."""
        self.workflow_step = step
        logger.debug(f"Set workflow step: {step}")
    
    def get_workflow_step(self) -> str:
        """Get the current workflow step."""
        return self.workflow_step
    
    def clear_business_data(self) -> None:
        """Clear all business data."""
        self.business_data.clear()
        logger.debug("Cleared all business data")
    
    def clear_recommendation_data(self) -> None:
        """Clear all recommendation data."""
        self.recommendation_data.clear()
        logger.debug("Cleared all recommendation data")

def create() -> State:
    """Create a new advisor agent state instance."""
    return State()
