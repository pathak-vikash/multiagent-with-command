from langgraph.graph import MessagesState
from typing import Dict, Any, Optional
from core.logger import logger

class State(MessagesState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.estimate_data: Dict[str, Any] = {}
        self.pricing_data: Dict[str, Any] = {}
        self.workflow_step: str = "initial"
    
    def set_estimate_data(self, key: str, value: Any) -> None:
        self.estimate_data[key] = value
    
    def get_estimate_data(self, key: str, default: Any = None) -> Any:
        return self.estimate_data.get(key, default)
    
    def set_pricing_data(self, key: str, value: Any) -> None:
        self.pricing_data[key] = value
    
    def get_pricing_data(self, key: str, default: Any = None) -> Any:
        return self.pricing_data.get(key, default)
    
    def set_workflow_step(self, step: str) -> None:
        self.workflow_step = step
    
    def get_workflow_step(self) -> str:
        return self.workflow_step
    
    def clear_estimate_data(self) -> None:
        self.estimate_data.clear()
    
    def clear_pricing_data(self) -> None:
        self.pricing_data.clear()

def create() -> State:
    return State()
