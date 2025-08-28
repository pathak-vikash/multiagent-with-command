"""
State management for the appointment sub-graph.

"""

from langgraph.graph import MessagesState
from typing import Dict, Any, Optional, List, TypedDict, Annotated
from operator import add
from core.logger import logger

# Following LangGraph's recommended TypedDict pattern for better performance
class AppointmentStateSchema(TypedDict):
    """Appointment state schema following LangGraph patterns"""
    messages: List[Any]  # Handled by MessagesState
    sop_data: Dict[str, Any]
    appointment_data: Dict[str, Any]
    workflow_step: str
    sop_history: Annotated[List[str], add]  # Use operator.add for list concatenation

class AppointmentState(MessagesState):
    """
    Extended state class for appointment sub-graph.
    
    Follows LangGraph's official state management patterns:
    - Extends MessagesState for proper message handling
    - Uses TypedDict for performance (as recommended in docs)
    - Minimal implementation with operators only where needed
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize with default values
        self["sop_data"] = {}
        self["appointment_data"] = {}
        self["workflow_step"] = "initial"
        self["sop_history"] = []
    
    def set_sop_data(self, sop_type: str, value: Any) -> None:
        """Set SOP data for a specific SOP type"""
        self["sop_data"][sop_type] = value
        # Add to SOP history using operator.add pattern
        current_history = self.get("sop_history", [])
        self["sop_history"] = add(current_history, [f"{sop_type}: {value}"])
        logger.debug(f"Set SOP data: {sop_type} = {value}")
    
    def get_sop_data(self, sop_type: str, default: Any = None) -> Any:
        """Get SOP data for a specific SOP type"""
        return self.get("sop_data", {}).get(sop_type, default)
    
    def is_sop_complete(self) -> bool:
        """Check if all required SOPs are complete"""
        required_sops = ['agenda', 'service', 'timing', 'location', 'contact']
        sop_data = self.get("sop_data", {})
        return all(
            sop_data.get(sop) is not None and sop_data.get(sop)
            for sop in required_sops
        )
    
    def get_missing_sops(self) -> List[str]:
        """Get list of missing SOPs"""
        required_sops = ['agenda', 'service', 'timing', 'location', 'contact']
        sop_data = self.get("sop_data", {})
        return [
            sop for sop in required_sops
            if not sop_data.get(sop) or not sop_data.get(sop)
        ]
    
    def set_appointment_data(self, key: str, value: Any) -> None:
        """Set appointment-specific data"""
        self["appointment_data"][key] = value
        logger.debug(f"Set appointment data: {key} = {value}")
    
    def get_appointment_data(self, key: str, default: Any = None) -> Any:
        """Get appointment-specific data"""
        return self.get("appointment_data", {}).get(key, default)
    
    def set_workflow_step(self, step: str) -> None:
        """Set the current workflow step"""
        self["workflow_step"] = step
        logger.debug(f"Set workflow step: {step}")

def create() -> AppointmentState:
    """Create a new appointment state instance"""
    return AppointmentState()
