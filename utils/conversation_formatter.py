from typing import List, Any, Optional
from core.logger import logger

def format_conversation_history(messages: List[Any], max_messages: Optional[int] = None) -> str:
    try:
        if not messages:
            return "No previous conversation history."
        
        if max_messages is not None:
            messages = messages[-max_messages:]
        
        formatted_messages = []
        for i, msg in enumerate(messages):
            try:
                content = msg.content if hasattr(msg, 'content') else str(msg)
                msg_type = msg.type if hasattr(msg, 'type') else 'unknown'
                
                if content and content.strip():
                    formatted_messages.append(f"{msg_type}: {content.strip()}")
                    
            except Exception as e:
                logger.warning(f"Error formatting message {i}: {str(e)}")
                continue
        
        if not formatted_messages:
            return "No readable conversation history found."
        
        return "\n".join(formatted_messages)
        
    except Exception as e:
        logger.error(f"Error formatting conversation history: {str(e)}")
        return "Error formatting conversation history."

def format_recent_conversation(messages: List[Any], exclude_last: int = 0) -> str:
    try:
        if not messages:
            return "No previous conversation history."
        
        if exclude_last > 0 and len(messages) > exclude_last:
            messages = messages[:-exclude_last]
        
        return format_conversation_history(messages)
        
    except Exception as e:
        logger.error(f"Error formatting recent conversation: {str(e)}")
        return "Error formatting conversation history."

def format_conversation_for_agent(messages: List[Any], agent_name: str) -> str:
    try:
        base_history = format_conversation_history(messages)
        return f"Previous conversation context for {agent_name}:\n{base_history}"
        
    except Exception as e:
        logger.error(f"Error formatting conversation for agent {agent_name}: {str(e)}")
        return f"Error formatting conversation history for {agent_name}."

def get_conversation_summary(messages: List[Any]) -> str:
    try:
        if not messages:
            return "No conversation history."
        
        message_count = len(messages)
        return f"Conversation has {message_count} message(s) in history."
        
    except Exception as e:
        logger.error(f"Error getting conversation summary: {str(e)}")
        return "Error getting conversation summary."
