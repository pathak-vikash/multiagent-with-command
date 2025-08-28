from langgraph.graph import MessagesState
from typing import Dict, Any, Optional
from core.logger import logger

class State(MessagesState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.routing_data: Dict[str, Any] = {}
        self.handoff_data: Dict[str, Any] = {}
        self.workflow_step: str = "initial"
    
    def set_routing_data(self, key: str, value: Any) -> None:
        self.routing_data[key] = value
    
    def get_routing_data(self, key: str, default: Any = None) -> Any:
        return self.routing_data.get(key, default)
    
    def set_handoff_data(self, key: str, value: Any) -> None:
        self.handoff_data[key] = value
    
    def get_handoff_data(self, key: str, default: Any = None) -> Any:
        return self.handoff_data.get(key, default)
    
    def set_workflow_step(self, step: str) -> None:
        self.workflow_step = step
    
    def get_workflow_step(self) -> str:
        return self.workflow_step
    
    def clear_routing_data(self) -> None:
        self.routing_data.clear()
    
    def clear_handoff_data(self) -> None:
        self.handoff_data.clear()

def create() -> State:
    return State()
