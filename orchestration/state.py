from langgraph.graph import MessagesState
from typing import Dict, Any, Optional, List, TypedDict, Annotated
from operator import add
from core.logger import logger

class OrchestrationState(TypedDict):
    messages: Annotated[List[Any], add]
    session_id: Optional[str]
    user_id: Optional[str]
    conversation_start: Optional[str]
    current_agent: Optional[str]
    routing_history: Annotated[List[str], add]
    workflow_step: str
    metadata: Dict[str, Any]

class State(MessagesState):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["session_id"] = None
        self["user_id"] = None
        self["conversation_start"] = None
        self["current_agent"] = None
        self["routing_history"] = []
        self["workflow_step"] = "initial"
        self["metadata"] = {}
    
    def add_routing_decision(self, agent_name: str) -> None:
        current_history = self.get("routing_history", [])
        self["routing_history"] = add(current_history, [agent_name])
        self["current_agent"] = agent_name
    
    def set_workflow_step(self, step: str) -> None:
        self["workflow_step"] = step

def create() -> State:
    return State()
