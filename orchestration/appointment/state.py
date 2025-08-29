from langgraph.graph import MessagesState
from langchain_core.messages import BaseMessage
from typing import Dict, Any, Optional, List, TypedDict, Annotated
from operator import add
from core.logger import logger

class AppointmentState(TypedDict):
    current: str
    messages: Annotated[List[BaseMessage], add]
    metadata: Dict[str, Any]
    should_route: bool
    sop_steps: Dict[str, Any]
    sop_history: Annotated[List[str], add]
    adherence_percentage: float  # Add adherence_percentage for compatibility


def create() -> AppointmentState:
    return AppointmentState(
        current="appointment",
        messages=[],
        metadata={},
        should_route=False,
        sop_steps={},
        sop_history=[],
        adherence_percentage=0.0
    )
