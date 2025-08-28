import traceback
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from langgraph.errors import ParentCommand
from utils.llm_helpers import create_llm_client
from utils.agent_handoff import get_handoff_tools
from utils.conversation_formatter import format_recent_conversation
from core.logger import logger
from .state import State

def supervisor(state) -> State:
    try:
        if not state["messages"]:
            return state
            
        last_message = state["messages"][-1]
        task_description = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        conversation_context = format_recent_conversation(state["messages"], exclude_last=1)
        
        if hasattr(state, 'set_workflow_step'):
            state.set_workflow_step("supervisor_routing")
        
        if hasattr(state, 'add_routing_decision'):
            state.add_routing_decision("supervisor")
        
        llm = create_llm_client()
        tools = get_handoff_tools()
        
        agent = create_react_agent(
            model=llm,
            tools=tools,
            prompt=(
                "You are a supervisor managing specialized agents. Your ONLY job is to route requests to the appropriate agent.\n\n"
                "Available agents:\n"
                "- general: For casual conversation, greetings, and general inquiries\n"
                "- appointment: For booking appointments, scheduling, and calendar management\n"
                "- support: For customer support, warranty claims, and technical issues\n"
                "- estimate: For price quotes, cost estimates, and pricing information\n"
                "- advisor: For business information, service details, and recommendations\n\n"
                "CRITICAL RULES:\n"
                "1. You MUST ALWAYS transfer to an agent - NEVER respond directly to the user\n"
                "2. You are NOT allowed to answer questions or provide information yourself\n"
                "3. Your ONLY action should be to use a handoff tool to transfer to the appropriate agent\n"
                "4. Provide a clear task description when transferring to an agent\n"
                "5. Transfer to one agent at a time, do not call agents in parallel\n\n"
                "Previous conversation context:\n"
                f"{conversation_context}\n\n"
                "Current user request: {task_description}\n\n"
                "Your task:\n"
                "- Analyze the user's intent and choose the most appropriate agent\n"
                "- Use the handoff tools to transfer to the selected agent\n"
                "- Provide clear task descriptions for the receiving agent\n"
                "- Be efficient and accurate in routing decisions\n\n"
                "REMEMBER: You are ONLY a router. Transfer the request to an agent immediately."
            ),
            name="supervisor"
        )
        
        response = agent.invoke(state)
        return response
        
    except ParentCommand as pc:
        raise
        
    except Exception as e:
        logger.error(f"Error in supervisor: {str(e)}")
        raise
