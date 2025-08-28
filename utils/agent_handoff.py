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

def get_handoff_tools():
    return [
        create_task_description_handoff_tool(
            agent_name="general",
            description="Transfer to general agent for casual conversation, greetings, and general inquiries."
        ),
        create_task_description_handoff_tool(
            agent_name="appointment", 
            description="Transfer to appointment agent for booking appointments, scheduling, and calendar management."
        ),
        create_task_description_handoff_tool(
            agent_name="support",
            description="Transfer to support agent for customer support, warranty claims, and technical issues."
        ),
        create_task_description_handoff_tool(
            agent_name="estimate",
            description="Transfer to estimate agent for price quotes, cost estimates, and pricing information."
        ),
        create_task_description_handoff_tool(
            agent_name="advisor",
            description="Transfer to advisor agent for business information, service details, and recommendations."
        )
    ]

def get_agent_descriptions():
    return {
        "general": "Handles casual conversation, greetings, and general inquiries",
        "appointment": "Handles appointment booking, scheduling, and calendar management", 
        "support": "Handles customer support, warranty claims, and technical issues",
        "estimate": "Handles price quotes, cost estimates, and pricing information",
        "advisor": "Handles business information, service details, and recommendations"
    }
