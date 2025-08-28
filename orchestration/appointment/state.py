from langgraph.graph import MessagesState
from typing import Dict, Any, Optional, List, TypedDict, Annotated
from operator import add
from core.logger import logger

class AppointmentStateSchema(TypedDict):
    messages: List[Any]
    sop_data: Dict[str, Any]
    appointment_data: Dict[str, Any]
    workflow_step: str
    sop_history: Annotated[List[str], add]

class AppointmentState(MessagesState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["sop_data"] = {}
        self["appointment_data"] = {}
        self["workflow_step"] = "initial"
        self["sop_history"] = []
    
    def set_sop_data(self, sop_type: str, value: Any) -> None:
        self["sop_data"][sop_type] = value
        current_history = self.get("sop_history", [])
        self["sop_history"] = add(current_history, [f"{sop_type}: {value}"])
    
    def get_sop_data(self, sop_type: str, default: Any = None) -> Any:
        return self.get("sop_data", {}).get(sop_type, default)
    
    def is_sop_complete(self) -> bool:
        required_sops = ['agenda', 'service', 'timing', 'location', 'contact']
        sop_data = self.get("sop_data", {})
        return all(
            sop_data.get(sop) is not None and sop_data.get(sop)
            for sop in required_sops
        )
    
    def get_missing_sops(self) -> List[str]:
        required_sops = ['agenda', 'service', 'timing', 'location', 'contact']
        sop_data = self.get("sop_data", {})
        return [
            sop for sop in required_sops
            if not sop_data.get(sop) or not sop_data.get(sop)
        ]
    
    def set_appointment_data(self, key: str, value: Any) -> None:
        self["appointment_data"][key] = value
    
    def get_appointment_data(self, key: str, default: Any = None) -> Any:
        return self.get("appointment_data", {}).get(key, default)
    
    def set_workflow_step(self, step: str) -> None:
        self["workflow_step"] = step

def create() -> AppointmentState:
    return AppointmentState()
