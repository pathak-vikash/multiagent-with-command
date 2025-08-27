"""
Estimate agent node following the official LangGraph pattern.
"""

import traceback
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import MessagesState
from schemas.intent_analysis import AgentType
from tools.estimate_tools import calculate_estimate, verify_address, get_service_catalog
from utils.llm_helpers import create_llm_client
from core.logger import logger

def estimate_agent_node(state: MessagesState) -> MessagesState:
    """Estimate agent node that handles price quotes and cost estimates"""
    
    try:
        logger.info("Estimate agent node starting")
        
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
        
        logger.info(f"Processing estimate task: {task_description[:100]}...")
        
        # Create LLM client
        llm = create_llm_client()
        
        # Create a prompt for estimate handling with tools
        prompt = ChatPromptTemplate.from_template("""
        You are an estimate agent with access to estimate tools. Your role is to:
        
        1. Handle price quotes, cost estimates, and pricing information
        2. Provide accurate pricing for services using the available tools
        3. Be professional and helpful
        4. Remember details from the conversation and build upon them
        
        Available tools:
        - calculate_estimate(service, location): Calculate service estimate
        - verify_address(address): Verify if address is in service area
        - get_service_catalog(): Get available services catalog
        
        Previous conversation context:
        {conversation_context}
        
        Current user request: {message}
        
        Instructions:
        - If the user wants a price quote, use the calculate_estimate tool
        - If the user provides an address, use the verify_address tool
        - If the user asks about available services, use the get_service_catalog tool
        - If the user is providing additional details for an estimate, acknowledge what you already know and ask for any missing information
        - If this is a new estimate request, ask for the necessary details
        - Be professional and reference previous parts of the conversation when relevant
        - If the user mentions specific services, locations, or requirements, acknowledge them
        
        Respond in a professional, helpful manner that builds upon the conversation context.
        """)
        
        # Create the agent with tools
        from langchain.agents import create_react_agent
        from langchain.agents import AgentExecutor
        
        # Get the tools
        tools = [calculate_estimate, verify_address, get_service_catalog]
        
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
        
        logger.info("Estimate agent provided response")
        logger.info("Estimate agent node completed successfully")
        return state
        
    except Exception as e:
        logger.error(f"Error in estimate agent node: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


