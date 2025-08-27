# Implementation Plan - LangGraph Way with Pydantic Schemas

## Overview

This document outlines the complete implementation plan for a multi-agent supervisor system using LangGraph with Pydantic schemas and `with_structured_output` for structured LLM responses. The system will handle five specialized agents: General, Appointment, Support, Estimate, and Advisor.

## System Architecture

```
User Input → Supervisor (LLM Intent Analysis) → Route to Agent → Agent Processing → Back to Supervisor → Response
```

**Five Specialized Agents:**
1. **General Agent** - Handles casual conversation, greetings, general chit-chat
2. **Appointment Agent** - Manages appointment booking and scheduling
3. **Support Agent** - Handles customer support and warranty claims
4. **Estimate Agent** - Handles price estimation and quotes
5. **Advisor Agent** - Provides business information and recommendations

## 1. **Pydantic Schemas for Structured Responses**

```python
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
    """Schema for LLM intent analysis response"""
    agent: AgentType = Field(description="Which agent should handle this request")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score for the routing decision")
    task_description: str = Field(description="Detailed description of what the agent should do")
    should_transfer: bool = Field(description="Whether to transfer to the agent or handle in supervisor")
    intent_type: IntentType = Field(description="Type of user intent")
    reasoning: str = Field(description="Brief explanation of why this agent was chosen")

class AppointmentDetails(BaseModel):
    """Schema for extracted appointment details"""
    service_type: Optional[str] = Field(default=None, description="Type of service requested")
    preferred_date: Optional[str] = Field(default=None, description="Preferred appointment date")
    preferred_time: Optional[str] = Field(default=None, description="Preferred appointment time")
    urgency: Literal["high", "medium", "low"] = Field(default="medium", description="Urgency level")
    additional_notes: Optional[str] = Field(default=None, description="Additional notes or requirements")
    contact_preference: Literal["phone", "email", "text"] = Field(default="phone", description="Preferred contact method")

class SupportDetails(BaseModel):
    """Schema for extracted support details"""
    issue_type: str = Field(description="Type of issue or problem")
    priority: Literal["high", "medium", "low"] = Field(default="medium", description="Priority level")
    warranty_related: bool = Field(default=False, description="Whether this is warranty-related")
    customer_id: Optional[str] = Field(default=None, description="Customer ID if available")
    description: str = Field(description="Detailed description of the issue")

class EstimateDetails(BaseModel):
    """Schema for extracted estimate details"""
    service_type: str = Field(description="Type of service for estimate")
    location: Optional[str] = Field(default=None, description="Service location")
    property_type: Optional[str] = Field(default=None, description="Type of property")
    urgency: Literal["high", "medium", "low"] = Field(default="medium", description="Urgency level")
    budget_range: Optional[str] = Field(default=None, description="Budget range if mentioned")

class AgentResponse(BaseModel):
    """Schema for agent response"""
    response: str = Field(description="The response message to the user")
    agent_type: AgentType = Field(description="Type of agent that generated the response")
    intent_type: IntentType = Field(description="Type of intent that was handled")
    handled_at: datetime = Field(default_factory=datetime.now, description="When the response was generated")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

class AppointmentResult(BaseModel):
    """Schema for appointment processing result"""
    response: str = Field(description="Response message to user")
    appointment_id: Optional[str] = Field(default=None, description="Generated appointment ID")
    status: Literal["confirmed", "pending", "failed"] = Field(description="Appointment status")
    scheduled_date: Optional[str] = Field(default=None, description="Scheduled date")
    scheduled_time: Optional[str] = Field(default=None, description="Scheduled time")
    service_type: Optional[str] = Field(default=None, description="Service type")
    agent_type: AgentType = Field(default=AgentType.APPOINTMENT_AGENT)

class SupportResult(BaseModel):
    """Schema for support processing result"""
    response: str = Field(description="Response message to user")
    ticket_id: Optional[str] = Field(default=None, description="Generated support ticket ID")
    status: Literal["open", "in_progress", "resolved"] = Field(description="Ticket status")
    priority: Literal["high", "medium", "low"] = Field(description="Ticket priority")
    estimated_resolution: Optional[str] = Field(default=None, description="Estimated resolution time")
    agent_type: AgentType = Field(default=AgentType.SUPPORT_AGENT)

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
```

## 2. **LangGraph State Schema**

```python
from langgraph.graph import StateGraph, START
from langgraph.types import MessagesState
from pydantic import Field

class CustomState(MessagesState):
    """Extended state with agent-specific data"""
    supervisor_decision: Optional[IntentAnalysis] = None
    general_result: Optional[AgentResponse] = None
    appointment_result: Optional[AppointmentResult] = None
    support_result: Optional[SupportResult] = None
    estimate_result: Optional[EstimateResult] = None
    advisor_result: Optional[AdvisorResult] = None
    current_agent: Optional[AgentType] = None
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    user_info: Dict[str, Any] = Field(default_factory=dict)
    session_data: Dict[str, Any] = Field(default_factory=dict)
```

## 3. **LLM-Powered Intent Analysis with LangGraph's with_structured_output**

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os

def create_intent_analyzer():
    """Create LLM-powered intent analyzer using LangGraph's with_structured_output"""
    
    # Create the LLM
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.1,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Create structured LLM with Pydantic output
    structured_llm = llm.with_structured_output(IntentAnalysis)
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_template("""
    You are an intelligent routing system that analyzes user messages and determines which specialized agent should handle their request.

    Available agents:
    1. general_agent - Handles casual conversation, greetings, general chit-chat, weather, jokes, etc.
    2. appointment_agent - Handles appointment booking, scheduling, calendar management, rescheduling
    3. support_agent - Handles customer support, warranty claims, technical issues, complaints, help requests
    4. estimate_agent - Handles price quotes, cost estimates, pricing information, service pricing
    5. advisor_agent - Handles business information, service details, company information, recommendations

    User message: {message}
    
    Conversation history: {conversation_history}

    Analyze the user's intent and determine the appropriate routing.
    
    Guidelines:
    - Choose the most appropriate agent based on the user's primary intent
    - If the message is general chit-chat, greetings, or casual conversation, use general_agent
    - If the message is about scheduling or appointments, use appointment_agent
    - If the message is about problems, help, or support, use support_agent
    - If the message is about pricing, quotes, or costs, use estimate_agent
    - If the message is about business information or services, use advisor_agent
    - Provide a clear task description for the chosen agent
    - Set should_transfer to true if the message requires specialized handling
    """)
    
    # Create the chain
    chain = prompt | structured_llm
    
    return chain

def analyze_user_intent_with_llm(message: str, conversation_history: List[Dict]) -> IntentAnalysis:
    """Use LLM with structured output for intent analysis"""
    
    try:
        # Create the analyzer
        intent_analyzer = create_intent_analyzer()
        
        # Analyze intent
        intent_analysis = intent_analyzer.invoke({
            "message": message,
            "conversation_history": json.dumps(conversation_history[-5:], indent=2)
        })
        
        return intent_analysis
        
    except Exception as e:
        # Fallback to general agent
        return IntentAnalysis(
            agent=AgentType.GENERAL_AGENT,
            confidence=0.5,
            task_description=f"Handle user message: {message}",
            should_transfer=True,
            intent_type=IntentType.GENERAL,
            reasoning=f"Fallback due to analysis error: {str(e)}"
        )
```

## 4. **Custom Tools System**

```python
def create_custom_tool(name: str, func: callable, description: str):
    """Create custom tools without LangChain dependencies"""
    
    def tool_wrapper(state: CustomState, **kwargs) -> Dict[str, Any]:
        try:
            result = func(**kwargs)
            return {
                "success": True,
                "result": result,
                "tool_name": name,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tool_name": name,
                "timestamp": datetime.now().isoformat()
            }
    
    tool_wrapper.__name__ = name
    tool_wrapper.__doc__ = description
    
    return tool_wrapper

# Appointment Tools
create_appointment_tool = create_custom_tool(
    name="create_appointment",
    func=lambda date, time, service: f"Appointment created for {service} on {date} at {time}",
    description="Create a new appointment"
)

check_availability_tool = create_custom_tool(
    name="check_availability",
    func=lambda date: f"Available slots on {date}: 9:00 AM, 2:00 PM, 4:00 PM",
    description="Check available appointment slots"
)

# Support Tools
create_support_ticket_tool = create_custom_tool(
    name="create_support_ticket",
    func=lambda issue, priority: f"Support ticket created for {issue} with priority {priority}",
    description="Create a new support ticket"
)

# Estimate Tools
calculate_estimate_tool = create_custom_tool(
    name="calculate_estimate",
    func=lambda service, location: f"Estimate for {service} at {location}: $500",
    description="Calculate service estimate"
)

# Advisor Tools
get_service_info_tool = create_custom_tool(
    name="get_service_info",
    func=lambda service: f"Information about {service}: [details]",
    description="Get information about services"
)
```

## 5. **Enhanced Agent Nodes with LangGraph's with_structured_output**

```python
from langgraph.types import Send, Command

def create_supervisor_node():
    """Create supervisor node with LLM-powered intent analysis"""
    
    def supervisor_node(state: CustomState) -> CustomState | Command:
        """Supervisor that routes to appropriate agents using LLM analysis"""
        
        # Get last user message
        last_message = state["messages"][-1]["content"]
        conversation_history = state.get("conversation_history", [])
        
        # Analyze intent with LLM
        intent_analysis = analyze_user_intent_with_llm(last_message, conversation_history)
        
        # Store decision in state
        state["supervisor_decision"] = intent_analysis
        
        # Log routing decision
        print(f"🔍 Intent Analysis: {intent_analysis.reasoning}")
        print(f"🔄 Routing to: {intent_analysis.agent} (confidence: {intent_analysis.confidence:.2f})")
        
        # Transfer to agent if needed
        if intent_analysis.should_transfer:
            agent_input = {
                "messages": [{"role": "user", "content": intent_analysis.task_description}],
                "context": state.get("context", {}),
                "user_info": state.get("user_info", {}),
                "conversation_history": conversation_history,
                "intent_analysis": intent_analysis
            }
            
            return Command(
                goto=[Send(intent_analysis.agent, agent_input)],
                graph=Command.PARENT,
            )
        
        return state
    
    return supervisor_node

def general_agent_node(state: CustomState) -> CustomState:
    """General agent with structured response"""
    
    last_message = state["messages"][-1]["content"]
    intent_analysis = state.get("intent_analysis")
    
    # Generate response
    response = generate_general_response_with_context(last_message, intent_analysis)
    
    # Create structured response
    agent_response = AgentResponse(
        response=response,
        agent_type=AgentType.GENERAL_AGENT,
        intent_type=intent_analysis.intent_type if intent_analysis else IntentType.GENERAL
    )
    
    # Update state
    state["general_result"] = agent_response
    state["current_agent"] = AgentType.GENERAL_AGENT
    state["messages"].append({
        "role": "assistant",
        "content": agent_response.response
    })
    
    return state

def appointment_agent_node(state: CustomState) -> CustomState:
    """Appointment agent with structured response"""
    
    last_message = state["messages"][-1]["content"]
    intent_analysis = state.get("intent_analysis")
    
    # Extract appointment details with LLM
    appointment_details = extract_appointment_details_with_llm(last_message)
    
    # Process appointment
    appointment_result = process_appointment_request(appointment_details)
    
    # Update state
    state["appointment_result"] = appointment_result
    state["current_agent"] = AgentType.APPOINTMENT_AGENT
    state["messages"].append({
        "role": "assistant",
        "content": appointment_result.response
    })
    
    return state

def extract_appointment_details_with_llm(message: str) -> AppointmentDetails:
    """Extract appointment details using LLM with structured output"""
    
    llm = ChatOpenAI(model="gpt-4", temperature=0.1)
    structured_llm = llm.with_structured_output(AppointmentDetails)
    
    prompt = ChatPromptTemplate.from_template("""
    Extract appointment details from the following message:
    "{message}"
    
    Extract the service type, preferred date/time, urgency level, and any additional notes.
    """)
    
    chain = prompt | structured_llm
    
    try:
        return chain.invoke({"message": message})
    except Exception as e:
        # Return default appointment details
        return AppointmentDetails(
            service_type="general service",
            urgency="medium",
            contact_preference="phone"
        )

def process_appointment_request(details: AppointmentDetails) -> AppointmentResult:
    """Process appointment request and return structured result"""
    
    # Mock appointment processing
    appointment_id = f"APT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    response = f"I've scheduled your {details.service_type} appointment"
    if details.preferred_date:
        response += f" for {details.preferred_date}"
    if details.preferred_time:
        response += f" at {details.preferred_time}"
    response += ". You'll receive a confirmation email shortly."
    
    return AppointmentResult(
        response=response,
        appointment_id=appointment_id,
        status="confirmed",
        scheduled_date=details.preferred_date,
        scheduled_time=details.preferred_time,
        service_type=details.service_type
    )

def support_agent_node(state: CustomState) -> CustomState:
    """Support agent with structured response"""
    
    last_message = state["messages"][-1]["content"]
    intent_analysis = state.get("intent_analysis")
    
    # Extract support details with LLM
    support_details = extract_support_details_with_llm(last_message)
    
    # Process support request
    support_result = process_support_request(support_details)
    
    # Update state
    state["support_result"] = support_result
    state["current_agent"] = AgentType.SUPPORT_AGENT
    state["messages"].append({
        "role": "assistant",
        "content": support_result.response
    })
    
    return state

def extract_support_details_with_llm(message: str) -> SupportDetails:
    """Extract support details using LLM with structured output"""
    
    llm = ChatOpenAI(model="gpt-4", temperature=0.1)
    structured_llm = llm.with_structured_output(SupportDetails)
    
    prompt = ChatPromptTemplate.from_template("""
    Extract support details from the following message:
    "{message}"
    
    Identify the issue type, priority level, whether it's warranty-related, and provide a detailed description.
    """)
    
    chain = prompt | structured_llm
    
    try:
        return chain.invoke({"message": message})
    except Exception as e:
        return SupportDetails(
            issue_type="general issue",
            priority="medium",
            description=message
        )

def process_support_request(details: SupportDetails) -> SupportResult:
    """Process support request and return structured result"""
    
    ticket_id = f"SUP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    response = f"I've created a support ticket for your {details.issue_type} issue. "
    if details.warranty_related:
        response += "Since this is warranty-related, our warranty team will contact you within 24 hours. "
    else:
        response += "Our support team will contact you within 48 hours. "
    response += f"Your ticket number is {ticket_id}."
    
    return SupportResult(
        response=response,
        ticket_id=ticket_id,
        status="open",
        priority=details.priority,
        estimated_resolution="24-48 hours"
    )

def estimate_agent_node(state: CustomState) -> CustomState:
    """Estimate agent with structured response"""
    
    last_message = state["messages"][-1]["content"]
    intent_analysis = state.get("intent_analysis")
    
    # Extract estimate details with LLM
    estimate_details = extract_estimate_details_with_llm(last_message)
    
    # Process estimate request
    estimate_result = process_estimate_request(estimate_details)
    
    # Update state
    state["estimate_result"] = estimate_result
    state["current_agent"] = AgentType.ESTIMATE_AGENT
    state["messages"].append({
        "role": "assistant",
        "content": estimate_result.response
    })
    
    return state

def extract_estimate_details_with_llm(message: str) -> EstimateDetails:
    """Extract estimate details using LLM with structured output"""
    
    llm = ChatOpenAI(model="gpt-4", temperature=0.1)
    structured_llm = llm.with_structured_output(EstimateDetails)
    
    prompt = ChatPromptTemplate.from_template("""
    Extract estimate details from the following message:
    "{message}"
    
    Identify the service type, location, property type, urgency level, and any budget information.
    """)
    
    chain = prompt | structured_llm
    
    try:
        return chain.invoke({"message": message})
    except Exception as e:
        return EstimateDetails(
            service_type="general service",
            urgency="medium"
        )

def process_estimate_request(details: EstimateDetails) -> EstimateResult:
    """Process estimate request and return structured result"""
    
    estimate_id = f"EST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Mock estimate calculation
    base_amount = 500
    if details.urgency == "high":
        base_amount += 100
    elif details.urgency == "low":
        base_amount -= 50
    
    response = f"Based on your {details.service_type} requirements"
    if details.location:
        response += f" at {details.location}"
    response += f", the estimated cost is ${base_amount}. "
    response += "This estimate is valid for 30 days. Would you like me to create a detailed quote?"
    
    return EstimateResult(
        response=response,
        estimate_id=estimate_id,
        amount=f"${base_amount}",
        validity_period="30 days",
        service_type=details.service_type
    )

def advisor_agent_node(state: CustomState) -> CustomState:
    """Advisor agent with structured response"""
    
    last_message = state["messages"][-1]["content"]
    intent_analysis = state.get("intent_analysis")
    
    # Generate advisor response
    advisor_result = generate_advisor_response(last_message)
    
    # Update state
    state["advisor_result"] = advisor_result
    state["current_agent"] = AgentType.ADVISOR_AGENT
    state["messages"].append({
        "role": "assistant",
        "content": advisor_result.response
    })
    
    return state

def generate_advisor_response(message: str) -> AdvisorResult:
    """Generate advisor response with structured output"""
    
    # Mock business information
    services = ["Lawn Care", "House Cleaning", "Pest Control", "Landscaping"]
    business_hours = "Monday-Friday: 8:00 AM - 6:00 PM, Saturday: 9:00 AM - 4:00 PM"
    contact_info = "Phone: (555) 123-4567, Email: info@example.com"
    
    response = f"We offer the following services: {', '.join(services)}. "
    response += f"Our business hours are {business_hours}. "
    response += f"You can reach us at {contact_info}. "
    response += "Is there a specific service you'd like to know more about?"
    
    return AdvisorResult(
        response=response,
        services_mentioned=services,
        business_hours=business_hours,
        contact_info=contact_info
    )

def generate_general_response_with_context(message: str, intent_analysis: Optional[IntentAnalysis]) -> str:
    """Generate contextual general responses based on intent analysis"""
    
    if not intent_analysis:
        return "Hello! I'm here to help with your business needs. What can I assist you with today?"
    
    intent_type = intent_analysis.intent_type
    
    if intent_type == IntentType.GREETING:
        return "Hello! I'm here to help with your business needs. I can assist with appointments, support, estimates, or general information. What would you like to do today?"
    
    elif intent_type == IntentType.FAREWELL:
        return "You're welcome! Feel free to reach out anytime if you need assistance with appointments, support, estimates, or any other business services. Have a great day!"
    
    else:
        return "I'm here to help! I can assist you with scheduling appointments, getting support, requesting estimates, or providing information about our services. What can I help you with today?"
```

## 6. **LangGraph Graph Construction**

```python
def create_supervisor_graph():
    """Create the complete supervisor graph with Pydantic schemas"""
    
    workflow = StateGraph(CustomState)
    
    # Add nodes
    workflow.add_node("supervisor", create_supervisor_node())
    workflow.add_node("general_agent", general_agent_node)
    workflow.add_node("appointment_agent", appointment_agent_node)
    workflow.add_node("support_agent", support_agent_node)
    workflow.add_node("estimate_agent", estimate_agent_node)
    workflow.add_node("advisor_agent", advisor_agent_node)
    
    # Add edges
    workflow.add_edge(START, "supervisor")
    
    # Add conditional edges from supervisor to agents
    workflow.add_conditional_edges(
        "supervisor",
        route_to_agent,
        {
            "general_agent": "general_agent",
            "appointment_agent": "appointment_agent",
            "support_agent": "support_agent",
            "estimate_agent": "estimate_agent",
            "advisor_agent": "advisor_agent"
        }
    )
    
    # All agents return to supervisor
    for agent in ["general_agent", "appointment_agent", "support_agent", "estimate_agent", "advisor_agent"]:
        workflow.add_edge(agent, "supervisor")
    
    return workflow.compile()

def route_to_agent(state: CustomState) -> str:
    """Route to appropriate agent based on supervisor decision"""
    
    supervisor_decision = state.get("supervisor_decision")
    if supervisor_decision and supervisor_decision.should_transfer:
        return supervisor_decision.agent
    
    return "supervisor"  # Default back to supervisor
```

## 7. **Main Application with Complete Implementation**

```python
import os
import json
from datetime import datetime
from dotenv import load_dotenv

def main():
    """Main application with complete implementation"""
    
    # Load environment variables
    load_dotenv()
    
    # Create the supervisor graph
    supervisor_graph = create_supervisor_graph()
    
    # Example conversations
    example_conversations = [
        "Hi there! How are you doing today?",
        "I need to book an appointment for lawn care next Tuesday afternoon",
        "My warranty claim was denied and I'm really frustrated about it",
        "What services do you offer and what are your business hours?",
        "Can you give me a quote for cleaning services at 123 Main Street?",
        "Thanks for your help, you've been great!",
        "What's the weather like today? Just curious!"
    ]
    
    # Process each example
    for message in example_conversations:
        print(f"\n{'='*60}")
        print(f"👤 User: {message}")
        print(f"{'='*60}")
        
        # Stream the conversation
        for chunk in supervisor_graph.stream({
            "messages": [{"role": "user", "content": message}],
            "conversation_history": [],
            "context": {},
            "user_info": {},
            "session_data": {}
        }):
            # Print the response
            if "messages" in chunk and len(chunk["messages"]) > 0:
                last_message = chunk["messages"][-1]
                if last_message["role"] == "assistant":
                    print(f"🤖 Assistant: {last_message['content']}")
                    
                    # Print structured data if available
                    current_agent = chunk.get("current_agent")
                    if current_agent:
                        print(f"🏷️ Handled by: {current_agent}")
                    
                    # Print additional context
                    if "supervisor_decision" in chunk:
                        decision = chunk["supervisor_decision"]
                        print(f"🎯 Intent: {decision.intent_type} (confidence: {decision.confidence:.2f})")
        
        print(f"{'='*60}")

if __name__ == "__main__":
    main()
```

## 8. **File Structure**

```
main.py (complete implementation)
agents/
  ├── supervisor.py (custom supervisor node)
  ├── general_agent.py (general conversation)
  ├── appointment_agent.py (appointment logic)
  ├── support_agent.py (support logic)
  ├── estimate_agent.py (estimate logic)
  └── advisor_agent.py (advisor logic)
tools/
  ├── appointment_tools.py (appointment tools)
  ├── support_tools.py (support tools)
  ├── estimate_tools.py (estimate tools)
  └── advisor_tools.py (advisor tools)
schemas/
  ├── __init__.py
  ├── intent_analysis.py (intent analysis schemas)
  ├── agent_responses.py (agent response schemas)
  └── business_models.py (business-specific schemas)
utils/
  ├── __init__.py
  ├── llm_helpers.py (LLM utilities)
  ├── state_management.py (state handling)
  └── response_generator.py (response generation)
tests/
  ├── test_supervisor.py
  ├── test_agents.py
  └── test_schemas.py
docs/
  ├── features.md (agent features)
  └── implementation-plan.md (this file)
requirements.txt
.env.example
README.md
```

## 9. **Dependencies**

```txt
langgraph>=0.2.0
langchain-openai>=0.1.0
langchain-core>=0.2.0
pydantic>=2.0.0
python-dotenv>=1.0.0
openai>=1.0.0
```

## 10. **Key Features**

1. **Pure LangGraph**: No LangChain dependencies for core functionality
2. **Structured Outputs**: Using `with_structured_output` for type-safe LLM responses
3. **Five Specialized Agents**: General, Appointment, Support, Estimate, Advisor
4. **LLM-Powered Intent Analysis**: Intelligent routing based on user intent
5. **Custom Tools**: Business-specific tools for each agent
6. **Pydantic Schemas**: Type-safe data structures throughout
7. **State Management**: Comprehensive state tracking and persistence
8. **Error Handling**: Robust error handling and fallbacks
9. **Conversation Flow**: Natural conversation with proper handoffs
10. **Extensible**: Easy to add new agents and tools

## 11. **Benefits of This Approach**

1. **Type Safety**: Compile-time validation of all data structures
2. **Structured Output**: Consistent, validated responses from LLM using `with_structured_output`
3. **LangGraph Integration**: Native support for Pydantic in LangGraph
4. **Error Handling**: Automatic validation and error messages
5. **Documentation**: Self-documenting schemas
6. **IDE Support**: Better autocomplete and type hints
7. **Serialization**: Easy JSON serialization/deserialization
8. **Validation**: Automatic data validation and sanitization
9. **Maintainability**: Clean, modular code structure
10. **Scalability**: Easy to extend with new agents and capabilities

## 12. **Testing Strategy**

1. **Unit Tests**: Test individual agents and functions
2. **Integration Tests**: Test agent interactions and routing
3. **Schema Tests**: Validate Pydantic schemas
4. **End-to-End Tests**: Test complete conversation flows
5. **Error Handling Tests**: Test fallback scenarios

This implementation plan provides a complete, scalable, and maintainable system that follows LangGraph best practices and uses structured outputs for reliable, type-safe LLM interactions.

## 13. **Implementation Steps**

### Phase 1: Foundation Setup
1. **Environment Setup**
   - Install dependencies
   - Set up environment variables
   - Create project structure

2. **Schema Implementation**
   - Implement all Pydantic schemas
   - Create type-safe data structures
   - Set up validation rules

3. **State Management**
   - Implement CustomState class
   - Set up state persistence
   - Create state utilities

### Phase 2: Core Components
4. **LLM Integration**
   - Implement intent analysis with `with_structured_output`
   - Create structured LLM chains
   - Set up error handling and fallbacks

5. **Agent Implementation**
   - Implement all five agent nodes
   - Create agent-specific tools
   - Set up agent response generation

6. **Supervisor Implementation**
   - Create supervisor node with routing logic
   - Implement Send/Command pattern
   - Set up conditional edges

### Phase 3: Integration & Testing
7. **Graph Construction**
   - Build complete StateGraph
   - Set up all edges and routing
   - Test graph compilation

8. **Testing & Validation**
   - Unit tests for all components
   - Integration tests for agent interactions
   - End-to-end conversation testing

9. **Documentation & Deployment**
   - Complete documentation
   - Example usage and demos
   - Deployment instructions

## 14. **Error Handling Strategy**

### LLM Error Handling
- **API Failures**: Fallback to default responses
- **Parsing Errors**: Use default schemas
- **Rate Limiting**: Implement retry logic
- **Timeout Handling**: Graceful degradation

### Agent Error Handling
- **Tool Failures**: Provide alternative responses
- **State Corruption**: Reset to safe state
- **Invalid Input**: Validate and sanitize
- **Network Issues**: Offline mode support

### Supervisor Error Handling
- **Routing Failures**: Default to general agent
- **Agent Unavailable**: Fallback mechanisms
- **State Issues**: Recovery procedures
- **Graph Errors**: Restart capabilities

## 15. **Performance Considerations**

### Optimization Strategies
1. **Caching**: Cache LLM responses for similar inputs
2. **Batching**: Batch multiple requests when possible
3. **Async Processing**: Use async/await for I/O operations
4. **Memory Management**: Efficient state handling
5. **Connection Pooling**: Reuse LLM connections

### Monitoring & Metrics
1. **Response Times**: Track agent response times
2. **Success Rates**: Monitor routing accuracy
3. **Error Rates**: Track failure patterns
4. **User Satisfaction**: Measure conversation quality
5. **Resource Usage**: Monitor system resources

## 16. **Security Considerations**

### Data Protection
1. **Input Sanitization**: Validate all user inputs
2. **Output Filtering**: Sanitize agent responses
3. **State Encryption**: Encrypt sensitive state data
4. **Access Control**: Implement proper authentication
5. **Audit Logging**: Log all interactions

### Privacy Compliance
1. **GDPR Compliance**: Handle personal data properly
2. **Data Retention**: Implement retention policies
3. **User Consent**: Get proper user consent
4. **Data Minimization**: Collect only necessary data
5. **Right to Deletion**: Implement data deletion

## 17. **Future Enhancements**

### Planned Features
1. **Multi-language Support**: Internationalization
2. **Voice Integration**: Speech-to-text and text-to-speech
3. **Advanced Analytics**: Conversation analytics and insights
4. **Custom Agent Training**: Domain-specific agent training
5. **Integration APIs**: Third-party system integrations

### Scalability Improvements
1. **Microservices Architecture**: Break into microservices
2. **Load Balancing**: Distribute load across instances
3. **Database Integration**: Persistent storage solutions
4. **Message Queues**: Async processing capabilities
5. **Containerization**: Docker and Kubernetes support

This comprehensive implementation plan ensures a robust, scalable, and maintainable multi-agent system that follows LangGraph best practices and provides excellent user experience.