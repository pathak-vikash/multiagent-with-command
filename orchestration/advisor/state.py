from langgraph.graph import MessagesState
from typing import Dict, Any, Optional
from core.logger import logger

class State(MessagesState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.business_data: Dict[str, Any] = {}
        self.recommendation_data: Dict[str, Any] = {}
        self.workflow_step: str = "initial"
    
    def set_business_data(self, key: str, value: Any) -> None:
        self.business_data[key] = value
    
    def get_business_data(self, key: str, default: Any = None) -> Any:
        return self.business_data.get(key, default)
    
    def set_recommendation_data(self, key: str, value: Any) -> None:
        self.recommendation_data[key] = value
    
    def get_recommendation_data(self, key: str, default: Any = None) -> Any:
        return self.recommendation_data.get(key, default)
    
    def set_workflow_step(self, step: str) -> None:
        self.workflow_step = step
    
    def get_workflow_step(self) -> str:
        return self.workflow_step
    
    def clear_business_data(self) -> None:
        self.business_data.clear()
    
    def clear_recommendation_data(self) -> None:
        self.recommendation_data.clear()

def create() -> State:
    return State()
