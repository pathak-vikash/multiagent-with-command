"""
Supervisor sub-graph nodes.

This module contains the supervisor agent node for routing and handoff management.
"""

import traceback
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from langgraph.errors import ParentCommand
from utils.llm_helpers import create_llm_client
from utils.agent_handoff import get_handoff_tools
from core.logger import logger
from .state import State

def supervisor(state) -> State:
    """Supervisor agent that routes requests to appropriate agents"""
    
    try:
        # Get all messages to understand the full conversation context
        if not state["messages"]:
            logger.warning("No messages in state")
            return state
            
        # Get the task description from the user (last message)
        last_message = state["messages"][-1]
        task_description = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        # Get the full conversation context
        conversation_context = ""
        if len(state["messages"]) > 1:
            # Include previous messages for context
            context_messages = state["messages"][:-1]
            conversation_context = "\n".join([
                f"{msg.type if hasattr(msg, 'type') else 'unknown'}: {msg.content if hasattr(msg, 'content') else str(msg)}"
                for msg in context_messages[-5:]  # Last 5 messages for context
            ])
        
        logger.info(f"🎯 Supervisor processing: {task_description[:50]}...")
        
        # Update state using LangGraph's recommended patterns
        if hasattr(state, 'set_workflow_step'):
            state.set_workflow_step("supervisor_routing")
        
        # Add routing decision to history
        if hasattr(state, 'add_routing_decision'):
            state.add_routing_decision("supervisor")
        
        # Create LLM client
        llm = create_llm_client()
        
        # Get the handoff tools
        tools = get_handoff_tools()
        
        # Create the supervisor agent using LangGraph pattern
        agent = create_react_agent(
            model=llm,
            tools=tools,
            prompt=(
                "You are a supervisor managing specialized agents:\n"
                "- general: For casual conversation, greetings, and general inquiries\n"
                "- appointment: For booking appointments, scheduling, and calendar management\n"
                "- support: For customer support, warranty claims, and technical issues\n"
                "- estimate: For price quotes, cost estimates, and pricing information\n"
                "- advisor: For business information, service details, and recommendations\n\n"
                "Analyze the user's request and transfer it to the most appropriate agent.\n"
                "Provide a clear task description when transferring to an agent.\n"
                "Do not do any work yourself - always delegate to the appropriate agent.\n"
                "Transfer to one agent at a time, do not call agents in parallel.\n\n"
                "Previous conversation context:\n"
                f"{conversation_context}\n\n"
                "Current user request: {task_description}\n\n"
                "Instructions:\n"
                "- Analyze the user's intent and choose the most appropriate agent\n"
                "- Use the handoff tools to transfer to the selected agent\n"
                "- Provide clear task descriptions for the receiving agent\n"
                "- Be efficient and accurate in routing decisions\n\n"
                "Respond by transferring to the appropriate agent."
            ),
            name="supervisor"
        )
        
        # Generate response
        response = agent.invoke(state)
        
        logger.info("✅ Supervisor completed")
        return response
        
    except ParentCommand as pc:
        # This is the expected behavior when handoff tools are used
        logger.info(f"🔄 Supervisor transferring to agent")
        # Re-raise the ParentCommand to let LangGraph handle the transfer
        raise
        
    except Exception as e:
        logger.error(f"❌ Error in supervisor: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
