from typing import Annotated
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command, Send
from langgraph.graph import MessagesState
from core.logger import logger

def create_handoff_tool(*, agent_name: str, description: str | None = None):
    name = f"transfer_to_{agent_name}"
    description = description or f"Ask {agent_name} for help."

    @tool(name, description=description)
    def handoff_tool(
        state: Annotated[MessagesState, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        tool_message = {
            "role": "tool",
            "content": f"Successfully transferred to {agent_name}",
            "name": name,
            "tool_call_id": tool_call_id,
        }
        return Command(
            goto=agent_name,  
            update={**state, "messages": state["messages"] + [tool_message]},  
            graph=Command.PARENT,  
        )

    return handoff_tool

def create_task_description_handoff_tool(*, agent_name: str, description: str | None = None):
    name = f"transfer_to_{agent_name}"
    description = description or f"Ask {agent_name} for help."

    @tool(name, description=description)
    def handoff_tool(
        task_description: Annotated[
            str,
            "Description of what the next agent should do, including all of the relevant context.",
        ],
        state: Annotated[MessagesState, InjectedState],
    ) -> Command:
        task_description_message = {"role": "user", "content": task_description}
        agent_input = {**state, "messages": [task_description_message]}
        return Command(
            goto=[Send(agent_name, agent_input)],
            graph=Command.PARENT,
        )

    return handoff_tool

@tool
def route_to_router(
    reason: Annotated[
        str,
        "Clear explanation of why routing to router is needed (e.g., 'User requested pricing information which is outside appointment agent scope', 'Unclear user intent requires router routing')"
    ],
    state: Annotated[MessagesState, InjectedState],
) -> Command:
    """Route the conversation to the router for proper agent selection when unsure or when request is outside current agent's scope. Available agents: general (conversation), appointment (scheduling), support (issues), estimate (pricing), advisor (information)."""
    # Find the original user request in the conversation history
    original_request = None
    for message in reversed(state.get("messages", [])):
        if hasattr(message, 'content') and message.content:
            # Skip routing messages and system messages
            if (hasattr(message, 'role') and message.role == 'user' and 
                not message.content.startswith("ROUTING REQUEST") and
                not message.content.startswith("The user is looking for")):
                original_request = message.content
                break
    
    if not original_request:
        # Fallback: look for any user message that's not a routing message
        for message in reversed(state.get("messages", [])):
            if (hasattr(message, 'content') and message.content and 
                hasattr(message, 'role') and message.role == 'user'):
                original_request = message.content
                break
    
    if not original_request:
        original_request = "No original request found"
    
    logger.info(f"Router tool found original request: {original_request}")
    
    # Create a message explaining the routing decision
    routing_message = {
        "role": "user", 
        "content": f"ROUTING REQUEST: {reason}\n\nUser's original request: {original_request}"
    }
    
    # Update state with routing context - preserve conversation history
    updated_messages = state.get("messages", []) + [routing_message]
    updated_state = {**state, "messages": updated_messages}
    
    logger.info(f"Agent routing to router: {reason}")
    
    return Command(
        goto="router",
        update=updated_state,
        graph=Command.PARENT,
    )

def get_handoff_tools():
    return [
        create_task_description_handoff_tool(
            agent_name="general",
            description="Help with general conversation and service information."
        ),
        create_task_description_handoff_tool(
            agent_name="appointment", 
            description="Help with booking appointments and scheduling services."
        ),
        create_task_description_handoff_tool(
            agent_name="support",
            description="Help with customer support and resolving issues."
        ),
        create_task_description_handoff_tool(
            agent_name="estimate",
            description="Help with pricing quotes and cost estimates."
        ),
        create_task_description_handoff_tool(
            agent_name="advisor",
            description="Help with business information and recommendations."
        )
    ]

def get_agent_router_tools():
    """Get router tools that agents can use to hand over to router."""
    return [
        route_to_router
    ]

def get_agent_descriptions():
    return {
        "general": "Handles casual conversation, greetings, general inquiries, and initial customer interactions. Can provide basic service information and route to specialized agents.",
        "appointment": "Specialized in appointment booking, scheduling, calendar management, availability checking, and rescheduling. Handles all time-related and scheduling requests.", 
        "support": "Specialized in customer support, warranty claims, technical issues, problem resolution, ticket creation, and escalation. Handles all customer service and issue-related requests.",
        "estimate": "Specialized in price quotes, cost estimates, pricing information, service catalogs, address verification, and financial calculations. Handles all pricing and cost-related requests.",
        "advisor": "Specialized in business information, service details, recommendations, business hours, contact information, and strategic advice. Handles all informational and advisory requests."
    }

def get_detailed_agent_capabilities():
    """Get detailed information about each agent's specific capabilities for routing decisions."""
    return {
        "general": {
            "primary_focus": "General conversation and initial customer interaction",
            "capabilities": [
                "Casual conversation and greetings",
                "Basic service information",
                "General inquiries about the business",
                "Initial customer assessment",
                "Routing to specialized agents"
            ],
            "keywords": ["hello", "hi", "greeting", "general", "basic", "overview", "introduction"]
        },
        "appointment": {
            "primary_focus": "Scheduling and time management",
            "capabilities": [
                "Book appointments and consultations",
                "Check availability and time slots",
                "Reschedule existing appointments",
                "Cancel appointments",
                "Calendar management",
                "Time-related queries"
            ],
            "keywords": ["book", "schedule", "appointment", "availability", "time", "calendar", "reschedule", "cancel", "when", "next week", "tomorrow"]
        },
        "support": {
            "primary_focus": "Problem resolution and customer service",
            "capabilities": [
                "Handle customer complaints",
                "Process warranty claims",
                "Create support tickets",
                "Escalate issues",
                "Technical problem resolution",
                "Customer service issues"
            ],
            "keywords": ["problem", "issue", "complaint", "warranty", "support", "help", "broken", "not working", "ticket", "escalate"]
        },
        "estimate": {
            "primary_focus": "Pricing and cost calculations",
            "capabilities": [
                "Calculate price estimates",
                "Provide cost quotes",
                "Verify service areas",
                "Get service catalogs",
                "Address verification",
                "Pricing information"
            ],
            "keywords": ["price", "cost", "estimate", "quote", "how much", "pricing", "address", "service area", "catalog"]
        },
        "advisor": {
            "primary_focus": "Information and recommendations",
            "capabilities": [
                "Provide business information",
                "Give service recommendations",
                "Share business hours",
                "Provide contact information",
                "Strategic advice",
                "Service details"
            ],
            "keywords": ["information", "recommendation", "advice", "hours", "contact", "details", "what services", "business info"]
        }
    }
