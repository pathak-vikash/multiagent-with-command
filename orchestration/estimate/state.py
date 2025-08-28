"""
State management for the estimate agent sub-graph.

This module defines the state structure and utilities
for managing estimate and pricing state.
"""

from langgraph.graph import MessagesState
from typing import Dict, Any, Optional
from core.logger import logger

class State(MessagesState):
    """
    Extended state class for estimate agent sub-graph.
    
    Includes estimate and pricing state management.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.estimate_data: Dict[str, Any] = {}
        self.pricing_data: Dict[str, Any] = {}
        self.workflow_step: str = "initial"
    
    def set_estimate_data(self, key: str, value: Any) -> None:
        """Set estimate-specific data."""
        self.estimate_data[key] = value
        logger.debug(f"Set estimate data: {key} = {value}")
    
    def get_estimate_data(self, key: str, default: Any = None) -> Any:
        """Get estimate-specific data."""
        return self.estimate_data.get(key, default)
    
    def set_pricing_data(self, key: str, value: Any) -> None:
        """Set pricing-specific data."""
        self.pricing_data[key] = value
        logger.debug(f"Set pricing data: {key} = {value}")
    
    def get_pricing_data(self, key: str, default: Any = None) -> Any:
        """Get pricing-specific data."""
        return self.pricing_data.get(key, default)
    
    def set_workflow_step(self, step: str) -> None:
        """Set the current workflow step."""
        self.workflow_step = step
        logger.debug(f"Set workflow step: {step}")
    
    def get_workflow_step(self) -> str:
        """Get the current workflow step."""
        return self.workflow_step
    
    def clear_estimate_data(self) -> None:
        """Clear all estimate data."""
        self.estimate_data.clear()
        logger.debug("Cleared all estimate data")
    
    def clear_pricing_data(self) -> None:
        """Clear all pricing data."""
        self.pricing_data.clear()
        logger.debug("Cleared all pricing data")

def create() -> State:
    """Create a new estimate agent state instance."""
    return State()
