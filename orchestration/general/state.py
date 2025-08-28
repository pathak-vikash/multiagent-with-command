from langgraph.graph import MessagesState
from typing import Dict, Any, Optional
from core.logger import logger

class State(MessagesState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversation_data: Dict[str, Any] = {}
        self.workflow_step: str = "initial"
    
    def set_conversation_data(self, key: str, value: Any) -> None:
        self.conversation_data[key] = value
    
    def get_conversation_data(self, key: str, default: Any = None) -> Any:
        return self.conversation_data.get(key, default)
    
    def set_workflow_step(self, step: str) -> None:
        self.workflow_step = step
    
    def get_workflow_step(self) -> str:
        return self.workflow_step
    
    def clear_conversation_data(self) -> None:
        self.conversation_data.clear()

def create() -> State:
    return State()
