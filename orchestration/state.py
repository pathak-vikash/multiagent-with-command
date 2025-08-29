from typing import Dict, Any, Optional, List, TypedDict, Annotated
from operator import add
from langchain_core.messages import BaseMessage
from core.logger import logger
from .schema import Node

class State(TypedDict):
    current: str
    messages: Annotated[List[BaseMessage], add]
    metadata: Dict[str, Any]
    routing_history: Annotated[List[str], add]
    sop_steps: Dict[str, Any]
    adherence_percentage: float
    should_route: bool

def create() -> State:
    return State(
        current=Node.APPOINTMENT.value,
        messages=[],
        metadata={},
        routing_history=[],
        sop_steps={},
        adherence_percentage=0.0,
        should_route=False
    )
