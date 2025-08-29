from pydantic import BaseModel, Field

class SOPStep(BaseModel):
    value: str = Field(
        default="",
        description="The value or result of the SOP step."
    )
    status: str = Field(
        default="pending",
        description="The status of the SOP step: 'completed', 'pending'."
    )
    reasoning: str = Field(
        default="",
        description="Explanation for why the step is marked with its current status."
    )
    description: str = Field(
        default="",
        description="A clear description of step and what is the purpose of that step."
    )
    question: str = Field(
        default="",
        description="The question to ask the user to complete the SOP step."
    )


class SOPSteps(BaseModel):
    agenda: SOPStep = Field(
        default=SOPStep(), 
        description="Purpose of the appointment."
    )
    service: SOPStep = Field(
        default=SOPStep(), 
        description="Type of service for which appointment is scheduled."
    )
    timing: SOPStep = Field(
        default=SOPStep(), 
        description="Timing of the appointment."
    )
    location: SOPStep = Field(
        default=SOPStep(), 
        description="Location to visit for service."
    )
    contact: SOPStep = Field(
        default=SOPStep(), 
        description="Preferred contact method for the appointment."
    )
    

class SOPExecutionResult(BaseModel):
    sop_steps: SOPSteps = Field(default=SOPSteps(), description="Collection of all required SOP steps.")
    
    adherence_percentage: int = Field(
        default=0,
        description="Calculated SOP adherence percentage (0-100)."
    )
    
    should_route: bool = Field(
        default=False, 
        description="True if all required SOP steps are complete and the routing decision is ready."
    )