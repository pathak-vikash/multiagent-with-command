"""
Advisor agent node following the official LangGraph pattern.
"""

import traceback
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import MessagesState
from schemas.intent_analysis import AgentType
from tools.advisor_tools import get_service_info, get_business_hours, get_contact_info
from utils.llm_helpers import create_llm_client
from core.logger import logger

def advisor_agent_node(state: MessagesState) -> MessagesState:
    """Advisor agent node that handles business information and recommendations"""
    
    try:
        logger.info("Advisor agent node starting")
        
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
        
        logger.info(f"Processing advisor task: {task_description[:100]}...")
        
        # Create LLM client
        llm = create_llm_client()
        
        # Create a prompt for advisor handling with tools
        prompt = ChatPromptTemplate.from_template("""
        You are an advisor agent with access to business information tools. Your role is to:
        
        1. Provide business information, service details, and recommendations
        2. Answer questions about company services and policies using the available tools
        3. Be knowledgeable and helpful
        4. Remember details from the conversation and build upon them
        
        Available tools:
        - get_service_info(service): Get detailed information about a specific service
        - get_business_hours(): Get business hours information
        - get_contact_info(): Get contact information
        
        Previous conversation context:
        {conversation_context}
        
        Current user request: {message}
        
        Instructions:
        - If the user asks about a specific service, use the get_service_info tool
        - If the user asks about business hours, use the get_business_hours tool
        - If the user asks for contact information, use the get_contact_info tool
        - If the user is asking follow-up questions about previously discussed services, reference the earlier conversation
        - If this is a new inquiry, provide comprehensive information
        - Be knowledgeable and reference previous parts of the conversation when relevant
        - If the user mentions specific services, policies, or previous discussions, acknowledge them
        
        Respond in a knowledgeable, helpful manner that builds upon the conversation context.
        """)
        
        # Create the agent with tools
        from langchain.agents import create_react_agent
        from langchain.agents import AgentExecutor
        
        # Get the tools
        tools = [get_service_info, get_business_hours, get_contact_info]
        
        # Create the agent
        agent = create_react_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
        # Generate response
        response = agent_executor.invoke({
            "message": task_description,
            "conversation_context": conversation_context
        })
        
        # Add the response to messages
        state["messages"].append({
            "role": "assistant",
            "content": response["output"]
        })
        
        logger.info("Advisor agent provided response")
        logger.info("Advisor agent node completed successfully")
        return state
        
    except Exception as e:
        logger.error(f"Error in advisor agent node: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


