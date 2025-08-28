"""
Base state management for the main orchestration level.
"""

from langgraph.graph import MessagesState
from typing import Dict, Any, Optional, List, TypedDict, Annotated
from operator import add
from core.logger import logger

# Following LangGraph's recommended TypedDict pattern for better performance
class OrchestrationState(TypedDict):
    """Main orchestration state schema following LangGraph patterns"""
    messages: Annotated[List[Any], add]  # Handled by MessagesState
    session_id: Optional[str]
    user_id: Optional[str]
    conversation_start: Optional[str]
    current_agent: Optional[str]
    routing_history: Annotated[List[str], add]  # Use operator.add for list concatenation
    workflow_step: str
    metadata: Dict[str, Any]

class State(MessagesState):
    """
    Extended state class for main orchestration level.
    
    Follows LangGraph's official state management patterns:
    - Extends MessagesState for proper message handling
    - Uses TypedDict for performance (as recommended in docs)
    - Minimal implementation with operators only where needed
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize with default values
        self["session_id"] = None
        self["user_id"] = None
        self["conversation_start"] = None
        self["current_agent"] = None
        self["routing_history"] = []
        self["workflow_step"] = "initial"
        self["metadata"] = {}
    
    def add_routing_decision(self, agent_name: str) -> None:
        """Add a routing decision to the history using operator.add pattern"""
        current_history = self.get("routing_history", [])
        self["routing_history"] = add(current_history, [agent_name])
        self["current_agent"] = agent_name
        logger.debug(f"Added routing decision: {agent_name}")
    
    def set_workflow_step(self, step: str) -> None:
        """Set the current workflow step"""
        self["workflow_step"] = step
        logger.debug(f"Set workflow step: {step}")

def create() -> State:
    """Create a new orchestration state instance"""
    return State()
