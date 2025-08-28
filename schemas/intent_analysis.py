from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
from enum import Enum

class IntentType(str, Enum):
    GREETING = "greeting"
    APPOINTMENT = "appointment"
    SUPPORT = "support"
    ESTIMATE = "estimate"
    INFORMATION = "information"
    GENERAL = "general"
    FAREWELL = "farewell"

class AgentType(str, Enum):
    GENERAL_AGENT = "general_agent"
    APPOINTMENT_AGENT = "appointment_agent"
    SUPPORT_AGENT = "support_agent"
    ESTIMATE_AGENT = "estimate_agent"
    ADVISOR_AGENT = "advisor_agent"

class IntentAnalysis(BaseModel):
    agent: AgentType = Field(description="Which agent should handle this request")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score for the routing decision")
    task_description: str = Field(description="Detailed description of what the agent should do")
    should_transfer: bool = Field(description="Whether to transfer to the agent or handle in supervisor")
    intent_type: IntentType = Field(description="Type of user intent")
    reasoning: str = Field(description="Brief explanation of why this agent was chosen")
