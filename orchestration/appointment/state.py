"""
State management for the appointment sub-graph.

This module defines the state structure and utilities
for managing appointment-specific state and SOP collection.
"""

from langgraph.graph import MessagesState
from typing import Dict, Any, Optional, List
from core.logger import logger

class AppointmentState(MessagesState):
    """
    Extended state class for appointment sub-graph.
    
    Includes appointment-specific state management for SOP collection
    and appointment booking workflow.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sop_data: Dict[str, Any] = {}
        self.appointment_data: Dict[str, Any] = {}
        self.workflow_step: str = "initial"
    
    def set_sop_data(self, sop_type: str, value: Any) -> None:
        """Set SOP data for a specific SOP type."""
        self.sop_data[sop_type] = value
        logger.debug(f"Set SOP data: {sop_type} = {value}")
    
    def get_sop_data(self, sop_type: str, default: Any = None) -> Any:
        """Get SOP data for a specific SOP type."""
        return self.sop_data.get(sop_type, default)
    
    def get_all_sop_data(self) -> Dict[str, Any]:
        """Get all collected SOP data."""
        return self.sop_data.copy()
    
    def is_sop_complete(self) -> bool:
        """Check if all required SOPs are complete."""
        required_sops = ['agenda', 'service', 'timing', 'location', 'contact']
        return all(sop in self.sop_data and self.sop_data[sop] for sop in required_sops)
    
    def set_appointment_data(self, key: str, value: Any) -> None:
        """Set appointment-specific data."""
        self.appointment_data[key] = value
        logger.debug(f"Set appointment data: {key} = {value}")
    
    def get_appointment_data(self, key: str, default: Any = None) -> Any:
        """Get appointment-specific data."""
        return self.appointment_data.get(key, default)
    
    def set_workflow_step(self, step: str) -> None:
        """Set the current workflow step."""
        self.workflow_step = step
        logger.debug(f"Set workflow step: {step}")
    
    def get_workflow_step(self) -> str:
        """Get the current workflow step."""
        return self.workflow_step
    
    def clear_sop_data(self) -> None:
        """Clear all SOP data."""
        self.sop_data.clear()
        logger.debug("Cleared all SOP data")
    
    def clear_appointment_data(self) -> None:
        """Clear all appointment data."""
        self.appointment_data.clear()
        logger.debug("Cleared all appointment data")

def create() -> AppointmentState:
    """Create a new appointment state instance."""
    return AppointmentState()
