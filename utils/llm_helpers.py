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

load_dotenv()

def initialize_langsmith():
    try:
        langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
        langsmith_project = os.getenv("LANGSMITH_PROJECT", "langgraph-multi-agent-system")
        langsmith_tracing = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
        
        if langsmith_api_key and langsmith_tracing:
            os.environ["LANGSMITH_TRACING"] = "true"
            os.environ["LANGSMITH_PROJECT"] = langsmith_project
            os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
            return True
        else:
            return False
            
    except Exception as e:
        logger.warning(f"Failed to initialize LangSmith: {str(e)}")
        return False

def create_llm_client() -> ChatOpenAI:
    try:
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.1"))
        
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    except Exception as e:
        logger.error(f"Failed to create LLM client: {str(e)}")
        raise

def create_intent_analyzer():
    try:
        llm = create_llm_client()
        structured_llm = llm.with_structured_output(IntentAnalysis, method="function_calling")
        
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
        
        chain = prompt | structured_llm
        return chain
        
    except Exception as e:
        logger.error(f"Failed to create intent analyzer: {str(e)}")
        raise

def analyze_user_intent_with_llm(message: str, conversation_history: List[Dict]) -> IntentAnalysis:
    start_time = time.time()
    
    try:
        intent_analyzer = create_intent_analyzer()
        
        intent_analysis = intent_analyzer.invoke({
            "message": message,
            "conversation_history": json.dumps(conversation_history[-5:], indent=2)
        })
        
        duration = time.time() - start_time
        logger.info(f"Intent analysis completed in {duration:.2f}s - Agent: {intent_analysis.agent.value}")
        
        return intent_analysis
        
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Intent analysis failed after {duration:.2f}s: {str(e)}")
        
        fallback_result = IntentAnalysis(
            agent=AgentType.GENERAL_AGENT,
            confidence=0.5,
            task_description=f"Handle user message: {message}",
            should_transfer=True,
            intent_type=IntentType.GENERAL,
            reasoning=f"Fallback due to analysis error: {str(e)}"
        )
        
        return fallback_result
