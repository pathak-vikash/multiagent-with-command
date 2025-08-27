from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
from .intent_analysis import AgentType, IntentType

class AgentResponse(BaseModel):
    """Schema for agent response"""
    response: str = Field(description="The response message to the user")
    agent_type: AgentType = Field(description="Type of agent that generated the response")
    intent_type: IntentType = Field(description="Type of intent that was handled")
    handled_at: datetime = Field(default_factory=datetime.now, description="When the response was generated")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

class AppointmentDetails(BaseModel):
    """Schema for extracted appointment details"""
    service_type: Optional[str] = Field(default=None, description="Type of service requested")
    preferred_date: Optional[str] = Field(default=None, description="Preferred appointment date")
    preferred_time: Optional[str] = Field(default=None, description="Preferred appointment time")
    urgency: Literal["high", "medium", "low"] = Field(default="medium", description="Urgency level")
    additional_notes: Optional[str] = Field(default=None, description="Additional notes or requirements")
    contact_preference: Literal["phone", "email", "text"] = Field(default="phone", description="Preferred contact method")

class AppointmentResult(BaseModel):
    """Schema for appointment processing result"""
    response: str = Field(description="Response message to user")
    appointment_id: Optional[str] = Field(default=None, description="Generated appointment ID")
    status: Literal["confirmed", "pending", "failed"] = Field(description="Appointment status")
    scheduled_date: Optional[str] = Field(default=None, description="Scheduled date")
    scheduled_time: Optional[str] = Field(default=None, description="Scheduled time")
    service_type: Optional[str] = Field(default=None, description="Service type")
    agent_type: AgentType = Field(default=AgentType.APPOINTMENT_AGENT)

class SupportDetails(BaseModel):
    """Schema for extracted support details"""
    issue_type: str = Field(description="Type of issue or problem")
    priority: Literal["high", "medium", "low"] = Field(default="medium", description="Priority level")
    warranty_related: bool = Field(default=False, description="Whether this is warranty-related")
    customer_id: Optional[str] = Field(default=None, description="Customer ID if available")
    description: str = Field(description="Detailed description of the issue")

class SupportResult(BaseModel):
    """Schema for support processing result"""
    response: str = Field(description="Response message to user")
    ticket_id: Optional[str] = Field(default=None, description="Generated support ticket ID")
    status: Literal["open", "in_progress", "resolved"] = Field(description="Ticket status")
    priority: Literal["high", "medium", "low"] = Field(description="Ticket priority")
    estimated_resolution: Optional[str] = Field(default=None, description="Estimated resolution time")
    agent_type: AgentType = Field(default=AgentType.SUPPORT_AGENT)

class EstimateDetails(BaseModel):
    """Schema for extracted estimate details"""
    service_type: str = Field(description="Type of service for estimate")
    location: Optional[str] = Field(default=None, description="Service location")
    property_type: Optional[str] = Field(default=None, description="Type of property")
    urgency: Literal["high", "medium", "low"] = Field(default="medium", description="Urgency level")
    budget_range: Optional[str] = Field(default=None, description="Budget range if mentioned")

class EstimateResult(BaseModel):
    """Schema for estimate processing result"""
    response: str = Field(description="Response message to user")
    estimate_id: Optional[str] = Field(default=None, description="Generated estimate ID")
    amount: Optional[str] = Field(default=None, description="Estimated amount")
    currency: str = Field(default="USD", description="Currency for the estimate")
    validity_period: Optional[str] = Field(default=None, description="How long the estimate is valid")
    service_type: Optional[str] = Field(default=None, description="Service type")
    agent_type: AgentType = Field(default=AgentType.ESTIMATE_AGENT)

class AdvisorResult(BaseModel):
    """Schema for advisor processing result"""
    response: str = Field(description="Response message to user")
    services_mentioned: List[str] = Field(default_factory=list, description="Services mentioned in response")
    business_hours: Optional[str] = Field(default=None, description="Business hours if mentioned")
    contact_info: Optional[str] = Field(default=None, description="Contact information if mentioned")
    agent_type: AgentType = Field(default=AgentType.ADVISOR_AGENT)

# Structured output schemas for LLM responses
class GeneralResponse(BaseModel):
    """Structured response for general agent"""
    response: str = Field(description="The response message to the user")
    intent_type: IntentType = Field(description="Type of intent that was handled")

class AppointmentResponse(BaseModel):
    """Structured response for appointment agent"""
    response: str = Field(description="Response message to user")
    appointment_id: str = Field(description="Generated appointment ID")
    status: Literal["confirmed", "pending", "failed"] = Field(description="Appointment status")
    scheduled_date: Optional[str] = Field(default=None, description="Scheduled date")
    scheduled_time: Optional[str] = Field(default=None, description="Scheduled time")
    service_type: str = Field(description="Service type")

class SupportResponse(BaseModel):
    """Structured response for support agent"""
    response: str = Field(description="Response message to user")
    ticket_id: str = Field(description="Generated support ticket ID")
    status: Literal["open", "in_progress", "resolved"] = Field(description="Ticket status")
    priority: Literal["high", "medium", "low"] = Field(description="Ticket priority")
    estimated_resolution: str = Field(description="Estimated resolution time")

class EstimateResponse(BaseModel):
    """Structured response for estimate agent"""
    response: str = Field(description="Response message to user")
    estimate_id: str = Field(description="Generated estimate ID")
    amount: str = Field(description="Estimated amount")
    currency: str = Field(default="USD", description="Currency for the estimate")
    validity_period: str = Field(description="How long the estimate is valid")
    service_type: str = Field(description="Service type")

class AdvisorResponse(BaseModel):
    """Structured response for advisor agent"""
    response: str = Field(description="Response message to user")
    services_mentioned: List[str] = Field(description="Services mentioned in response")
    business_hours: str = Field(description="Business hours if mentioned")
    contact_info: str = Field(description="Contact information if mentioned")
