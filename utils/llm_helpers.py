import os
import json
import time
import traceback
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from schemas.intent_analysis import IntentAnalysis, IntentType, AgentType
from core.logger import logger

# Load environment variables from .env file
load_dotenv()

def initialize_langsmith():
    """Initialize LangSmith configuration for tracing and monitoring"""
    try:
        # Check if LangSmith is configured
        langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
        langsmith_project = os.getenv("LANGSMITH_PROJECT", "langgraph-multi-agent-system")
        langsmith_tracing = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
        
        if langsmith_api_key and langsmith_tracing:
            # Set LangSmith environment variables
            os.environ["LANGSMITH_TRACING"] = "true"
            os.environ["LANGSMITH_PROJECT"] = langsmith_project
            os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
            
            logger.info(f"🔍 LangSmith tracing enabled for project: {langsmith_project}")
            logger.info(f"📊 View traces at: https://smith.langchain.com/o/default/projects/p/{langsmith_project}")
            return True
        else:
            logger.info("🔍 LangSmith tracing disabled (set LANGSMITH_API_KEY and LANGSMITH_TRACING=true to enable)")
            return False
            
    except Exception as e:
        logger.warning(f"Failed to initialize LangSmith: {str(e)}")
        return False

def create_llm_client() -> ChatOpenAI:
    """Create and configure the LLM client"""
    try:
        # Get configuration from environment variables with defaults
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))
        
        logger.info(f"Creating LLM client with model={model}, temperature={temperature}")
        
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    except Exception as e:
        logger.error(f"Failed to create LLM client: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

def create_intent_analyzer():
    """Create LLM-powered intent analyzer using LangGraph's with_structured_output"""
    
    try:
        logger.info("Creating intent analyzer")
        
        # Create the LLM
        llm = create_llm_client()
        
        # Create structured LLM with Pydantic output using function calling
        structured_llm = llm.with_structured_output(IntentAnalysis, method="function_calling")
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_template("""
        You are an intelligent routing system that analyzes user messages and determines which specialized agent should handle their request.

        Available agents:
        1. general_agent - Handles casual conversation, greetings, general chit-chat, weather, jokes, etc.
        2. appointment_agent - Handles appointment booking, scheduling, calendar management, rescheduling
        3. support_agent - Handles customer support, warranty claims, technical issues, complaints, help requests
        4. estimate_agent - Handles price quotes, cost estimates, pricing information, service pricing
        5. advisor_agent - Handles business information, service details, company information, recommendations

        User message: {message}
        
        Conversation history: {conversation_history}

        Analyze the user's intent and determine the appropriate routing.
        
        Guidelines:
        - Choose the most appropriate agent based on the user's primary intent
        - If the message is general chit-chat, greetings, or casual conversation, use general_agent
        - If the message is about scheduling or appointments, use appointment_agent
        - If the message is about problems, help, or support, use support_agent
        - If the message is about pricing, quotes, or costs, use estimate_agent
        - If the message is about business information or services, use advisor_agent
        - Provide a clear task description for the chosen agent
        - ALWAYS set should_transfer to true - all messages should be handled by the appropriate specialized agent
        - The supervisor should never handle messages directly, only route them
        """)
        
        # Create the chain
        chain = prompt | structured_llm
        
        logger.info("Intent analyzer created successfully")
        return chain
        
    except Exception as e:
        logger.error(f"Failed to create intent analyzer: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

def analyze_user_intent_with_llm(message: str, conversation_history: List[Dict]) -> IntentAnalysis:
    """Use LLM with structured output for intent analysis"""
    
    start_time = time.time()
    
    try:
        logger.info(f"Starting intent analysis for message: {message[:100]}...")
        
        # Create the analyzer
        intent_analyzer = create_intent_analyzer()
        
        # Analyze intent
        intent_analysis = intent_analyzer.invoke({
            "message": message,
            "conversation_history": json.dumps(conversation_history[-5:], indent=2)
        })
        
        duration = time.time() - start_time
        
        # Log the intent analysis result
        logger.info(f"Intent analysis completed in {duration:.2f}s - Agent: {intent_analysis.agent.value}, Confidence: {intent_analysis.confidence:.2f}")
        logger.info(f"Intent analysis completed: {intent_analysis.intent_type} -> {intent_analysis.agent_type}")
        
        return intent_analysis
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Intent analysis failed after {duration:.2f}s: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Fallback to general agent
        fallback_result = IntentAnalysis(
            agent=AgentType.GENERAL_AGENT,
            confidence=0.5,
            task_description=f"Handle user message: {message}",
            should_transfer=True,
            intent_type=IntentType.GENERAL,
            reasoning=f"Fallback due to analysis error: {str(e)}"
        )
        
        logger.warning(f"Using fallback intent analysis: {fallback_result.agent.value}")
        return fallback_result
