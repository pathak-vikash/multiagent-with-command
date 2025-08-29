import traceback
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from tools.advisor_tools import get_service_info, get_business_hours, get_contact_info
from utils.llm_helpers import create_llm_client
from utils.helper import format_conversation_history
from utils.agent_handoff import get_agent_router_tools
from core.logger import logger
from .state import State

def advisor_agent(state) -> State:
    try:
        if not state["messages"]:
            return state
            
        last_message = state["messages"][-1]
        task_description = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        conversation_context = format_conversation_history(state["messages"])
        
        if hasattr(state, 'set_workflow_step'):
            state.set_workflow_step("business_advice")
        
        llm = create_llm_client()
        
        # Include both advisor tools and router tools
        advisor_tools = [get_service_info, get_business_hours, get_contact_info]
        router_tools = get_agent_router_tools()
        all_tools = advisor_tools + router_tools
        
        agent = create_react_agent(
            model=llm,
            tools=all_tools,
            prompt=(
                "You are an advisor agent with access to business information tools. Your role is to:\n"
                "1. Provide business information and recommendations\n"
                "2. Share service details and capabilities\n"
                "3. Provide business hours and contact information\n"
                "4. Be knowledgeable and helpful\n"
                "5. Route to router when requests are outside your scope\n\n"
                "Available tools:\n"
                "- get_service_info(service_type): Get detailed service information\n"
                "- get_business_hours(): Get current business hours\n"
                "- get_contact_info(): Get contact information\n"
                "- route_to_router(reason): Route to router when request is outside advisor scope\n\n"
                "When to route to router:\n"
                "- User asks about appointment booking → Route to appointment agent (scheduling specialist)\n"
                "- User asks about support issues → Route to support agent (issue resolution specialist)\n"
                "- User asks about pricing or estimates → Route to estimate agent (pricing specialist)\n"
                "- User asks general questions → Route to general agent (conversation specialist)\n"
                "- Unclear or ambiguous requests → Route to router for proper agent selection\n\n"
                "Previous conversation context:\n"
                f"{conversation_context}\n\n"
                "Current user request: {task_description}\n\n"
                "Instructions:\n"
                "- If the user asks about services, use get_service_info\n"
                "- If the user asks about hours, use get_business_hours\n"
                "- If the user asks about contact info, use get_contact_info\n"
                "- If the request is outside advisor scope, use route_to_router\n"
                "- Provide helpful recommendations based on user needs\n"
                "- Remember details from the conversation and build upon them\n\n"
                "Respond in a helpful, professional manner that builds upon the conversation context."
            ),
            name="advisor_agent"
        )
        
        response = agent.invoke(state)
        return response
        
    except Exception as e:
        logger.error(f"Error in advisor agent: {str(e)}")
        raise
