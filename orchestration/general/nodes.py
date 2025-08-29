import traceback
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from utils.llm_helpers import create_llm_client
from utils.helper import format_conversation_history
from core.logger import logger
from .state import State

def general_agent(state) -> State:
    try:
        if not state["messages"]:
            return state
            
        last_message = state["messages"][-1]
        task_description = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        conversation_context = format_conversation_history(state["messages"])
        
        if hasattr(state, 'set_workflow_step'):
            state.set_workflow_step("general_conversation")
        
        llm = create_llm_client()
        
        agent = create_react_agent(
            model=llm,
            tools=[],
            prompt=(
                "You are a friendly and helpful general conversation agent. Your role is to:\n"
                "1. Handle casual conversation, greetings, and general inquiries\n"
                "2. Be warm, welcoming, and engaging\n"
                "3. Remember details from the conversation and build upon them\n"
                "4. Help users feel comfortable and heard\n\n"
                "Previous conversation context:\n"
                f"{conversation_context}\n\n"
                "Current user request: {task_description}\n\n"
                "Instructions:\n"
                "- Be conversational and friendly\n"
                "- Reference previous parts of the conversation when relevant\n"
                "- If the user asks about specific services, politely redirect them to the appropriate agent\n"
                "- Keep responses engaging but concise\n"
                "- Show genuine interest in the user's needs\n\n"
                "Respond in a warm, helpful manner that builds upon the conversation context."
            ),
            name="general_agent"
        )
        
        response = agent.invoke(state)
        return response
        
    except Exception as e:
        logger.error(f"Error in general agent: {str(e)}")
        raise
