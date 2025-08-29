import os
import json
import time
import traceback
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
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
