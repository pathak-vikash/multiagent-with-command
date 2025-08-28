import traceback
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from tools.estimate_tools import calculate_estimate, verify_address, get_service_catalog
from utils.llm_helpers import create_llm_client
from utils.conversation_formatter import format_recent_conversation
from core.logger import logger
from .state import State

def estimate_agent(state) -> State:
    try:
        if not state["messages"]:
            return state
            
        last_message = state["messages"][-1]
        task_description = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        conversation_context = format_recent_conversation(state["messages"], exclude_last=1)
        
        if hasattr(state, 'set_workflow_step'):
            state.set_workflow_step("estimate_calculation")
        
        llm = create_llm_client()
        tools = [calculate_estimate, verify_address, get_service_catalog]
        
        agent = create_react_agent(
            model=llm,
            tools=tools,
            prompt=(
                "You are an estimate agent with access to pricing tools. Your role is to:\n"
                "1. Calculate price estimates for services\n"
                "2. Verify addresses for service areas\n"
                "3. Provide service catalog information\n"
                "4. Be professional and accurate\n\n"
                "Available tools:\n"
                "- calculate_estimate(service_type, address, details): Calculate price estimate\n"
                "- verify_address(address): Verify if address is in service area\n"
                "- get_service_catalog(): Get available services and pricing\n\n"
                "Previous conversation context:\n"
                f"{conversation_context}\n\n"
                "Current user request: {task_description}\n\n"
                "Instructions:\n"
                "- If the user wants a price estimate, use calculate_estimate\n"
                "- If the user provides an address, verify it with verify_address\n"
                "- If the user asks about services, use get_service_catalog\n"
                "- Provide clear, accurate pricing information\n"
                "- Remember details from the conversation and build upon them\n\n"
                "Respond in a helpful, professional manner that builds upon the conversation context."
            ),
            name="estimate_agent"
        )
        
        response = agent.invoke(state)
        return response
        
    except Exception as e:
        logger.error(f"Error in estimate agent: {str(e)}")
        raise
