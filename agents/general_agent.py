"""
General agent node following the official LangGraph pattern.
"""

import traceback
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import MessagesState
from schemas.agent_responses import AgentResponse
from schemas.intent_analysis import AgentType, IntentType
from utils.llm_helpers import create_llm_client
from core.logger import logger

def general_agent_node(state: MessagesState) -> MessagesState:
    """General agent node that handles casual conversation"""
    
    try:
        logger.info("General agent node starting")
        
        # Get all messages to understand the full conversation context
        if not state["messages"]:
            logger.warning("No messages in state")
            return state
            
        # Get the task description from the supervisor (last message)
        last_message = state["messages"][-1]
        task_description = last_message.get("content", "")
        
        # Get the full conversation context
        conversation_context = ""
        if len(state["messages"]) > 1:
            # Include previous messages for context (skip the supervisor's task description)
            context_messages = state["messages"][:-1]
            conversation_context = "\n".join([
                f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
                for msg in context_messages[-5:]  # Last 5 messages for context
            ])
        
        logger.info(f"Processing general task: {task_description[:100]}...")
        
        # Create LLM client
        llm = create_llm_client()
        
        # Create a prompt for general conversation with context
        prompt = ChatPromptTemplate.from_template("""
        You are a friendly general conversation agent. Your role is to:
        
        1. Handle casual conversation, greetings, and general inquiries
        2. Provide friendly, helpful responses
        3. Be polite and welcoming
        4. Remember details from the conversation and build upon them
        
        Previous conversation context:
        {conversation_context}
        
        Current user message: {message}
        
        Instructions:
        - If the user asks about specific business services (appointments, support, pricing, business info), 
          politely redirect them to the appropriate department
        - Be conversational and reference previous parts of the conversation when relevant
        - Maintain a friendly, helpful tone throughout the conversation
        
        Respond in a friendly, helpful manner that builds upon the conversation context.
        """)
        
        # Generate response
        chain = prompt | llm
        response = chain.invoke({
            "message": task_description,
            "conversation_context": conversation_context
        })
        
        # Add the response to messages
        state["messages"].append({
            "role": "assistant",
            "content": response.content
        })
        
        logger.info("General agent provided response")
        logger.info("General agent node completed successfully")
        return state
        
    except Exception as e:
        logger.error(f"Error in general agent node: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise
