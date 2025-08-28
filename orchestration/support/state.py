from langgraph.graph import MessagesState
from typing import Dict, Any, Optional
from core.logger import logger

class State(MessagesState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.support_data: Dict[str, Any] = {}
        self.ticket_data: Dict[str, Any] = {}
        self.workflow_step: str = "initial"
    
    def set_support_data(self, key: str, value: Any) -> None:
        self.support_data[key] = value
    
    def get_support_data(self, key: str, default: Any = None) -> Any:
        return self.support_data.get(key, default)
    
    def set_ticket_data(self, key: str, value: Any) -> None:
        self.ticket_data[key] = value
    
    def get_ticket_data(self, key: str, default: Any = None) -> Any:
        return self.ticket_data.get(key, default)
    
    def set_workflow_step(self, step: str) -> None:
        self.workflow_step = step
    
    def get_workflow_step(self) -> str:
        return self.workflow_step
    
    def clear_support_data(self) -> None:
        self.support_data.clear()
    
    def clear_ticket_data(self) -> None:
        self.ticket_data.clear()

def create() -> State:
    return State()
