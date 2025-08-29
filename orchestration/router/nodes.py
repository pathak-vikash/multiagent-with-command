import traceback
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from langgraph.errors import ParentCommand
from utils.llm_helpers import create_llm_client
from utils.agent_handoff import get_handoff_tools
from utils.helper import format_conversation_history
from core.logger import logger
from orchestration.state import State
from orchestration.schema import Node

def router(state) -> State:
    try:
        if not state["messages"]:
            return state
            
        last_message = state["messages"][-1]
        task_description = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        conversation_context = format_conversation_history(state["messages"])
        
        if hasattr(state, 'current'):
            state.current = Node.ROUTER.value
        
        if hasattr(state, 'add_routing_decision'):
            state.add_routing_decision("router")
        
        llm = create_llm_client()
        tools = get_handoff_tools()
        
        agent = create_react_agent(
            model=llm,
            tools=tools,
            prompt=(
                "You are a router managing specialized agents. Your ONLY job is to route requests to the appropriate agent.\n\n"
                "Available agents:\n"
                "- general: For casual conversation, greetings, general inquiries, and initial customer interactions\n"
                "- appointment: For booking appointments, scheduling, calendar management, availability checking, and rescheduling\n"
                "- support: For customer support, warranty claims, technical issues, problem resolution, and ticket creation\n"
                "- estimate: For price quotes, cost estimates, pricing information, service catalogs, and address verification\n"
                "- advisor: For business information, service details, recommendations, business hours, and contact information\n\n"
                "CRITICAL RULES:\n"
                "1. You MUST ALWAYS transfer to an agent - NEVER respond directly to the user\n"
                "2. You are NOT allowed to answer questions or provide information yourself\n"
                "3. Your ONLY action should be to use a handoff tool to transfer to the appropriate agent\n"
                "4. Provide a clear task description when transferring to an agent\n"
                "5. Transfer to one agent at a time, do not call agents in parallel\n"
                "6. If a request comes from another agent (routing request), analyze the reason and route appropriately\n\n"
                "ROUTING GUIDELINES:\n"
                "- If the request mentions 'ROUTING REQUEST:', look at the conversation history to find the original user request\n"
                "- Route based on the original user request, not the routing reason\n"
                "- Look for the user's actual intent in the conversation history\n"
                "- Consider the full context when making routing decisions\n"
                "- If unclear, route to the general agent for initial assessment\n\n"
                "IMPORTANT: When you see 'ROUTING REQUEST:', the original user request will be shown after 'User's original request:'\n"
                "Use that original request to determine which agent to route to.\n\n"
                "Previous conversation context:\n"
                f"{conversation_context}\n\n"
                "Current user request: {task_description}\n\n"
                "Your task:\n"
                "- Analyze the user's intent and choose the most appropriate agent\n"
                "- Use the handoff tools to transfer to the selected agent\n"
                "- Provide clear task descriptions for the receiving agent\n"
                "- Be efficient and accurate in routing decisions\n"
                "- If you see 'ROUTING REQUEST:', find the original user request in the conversation history\n\n"
                "REMEMBER: You are ONLY a router. Transfer the request to an agent immediately."
            ),
            name="router"
        )
        
        response = agent.invoke(state)
        return response
        
    except ParentCommand as pc:
        raise
        
    except Exception as e:
        logger.error(f"Error in router: {str(e)}")
        raise
