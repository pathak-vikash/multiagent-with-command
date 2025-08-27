"""
Supervisor agent following the official LangGraph supervisor pattern.
Based on the supervisor-tools.py example from LangGraph documentation.
"""

import traceback
from langgraph.prebuilt import create_react_agent
from langgraph.graph import MessagesState
from langgraph.errors import ParentCommand
from utils.llm_helpers import create_llm_client
from utils.agent_handoff import get_handoff_tools
from core.logger import logger

def create_supervisor_agent():
    """Create supervisor agent using the official LangGraph pattern"""
    
    # Create the supervisor agent using the reference pattern
    supervisor_agent = create_react_agent(
        model=create_llm_client(),
        tools=get_handoff_tools(),
        prompt=(
            "You are a supervisor managing specialized agents:\n"
            "- general_agent: For casual conversation, greetings, and general inquiries\n"
            "- appointment_agent: For booking appointments, scheduling, and calendar management\n"
            "- support_agent: For customer support, warranty claims, and technical issues\n"
            "- estimate_agent: For price quotes, cost estimates, and pricing information\n"
            "- advisor_agent: For business information, service details, and recommendations\n\n"
            "Analyze the user's request and transfer it to the most appropriate agent.\n"
            "Provide a clear task description when transferring to an agent.\n"
            "Do not do any work yourself - always delegate to the appropriate agent.\n"
            "Transfer to one agent at a time, do not call agents in parallel."
        ),
        name="supervisor"
    )
    
    return supervisor_agent

def supervisor_node(state: MessagesState) -> MessagesState:
    """Supervisor node function that can be used in the graph"""
    
    try:
        logger.info("Supervisor node starting")
        
        # Create the supervisor agent
        supervisor_agent = create_supervisor_agent()
        
        # Run the supervisor agent
        result = supervisor_agent.invoke(state)
        
        logger.info("Supervisor node completed successfully")
        return result
        
    except ParentCommand as pc:
        # This is the expected behavior when handoff tools are used
        logger.info(f"Supervisor transferring to agent via ParentCommand")
        # Re-raise the ParentCommand to let LangGraph handle the transfer
        raise
        
    except Exception as e:
        logger.error(f"Error in supervisor node: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
