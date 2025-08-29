import json
import pytz
import traceback
import xml.etree.ElementTree as ET
from datetime import datetime
from dateutil import parser
from collections.abc import Mapping
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from typing import List, Dict, Any, Union
from pydantic import BaseModel

from dotty_dictionary import dotty
from core.logger import logger

def union_lists(*lists) -> List:
    """Union of multiple lists."""
    return list(set().union(*lists))

def subract_lists(list1, list2) -> List:
    """Subtract list2 from list1."""
    return list(set(list1) - set(list2))

def merge_dicts(original, updates):
    result = original.copy()
    for key in original:
        if key in updates:
            result[key] = updates[key]
    return result

def read_file(file_path, encoding='utf-8'):
    """Read content from a file based on its extension."""
    try:
        if file_path.endswith('.json'):
            with open(file_path, 'r', encoding=encoding) as file:
                return dotty(json.load(file))
        elif file_path.endswith('.md'):
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()
        elif file_path.endswith('.txt'):
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()
        else:
            error_msg = "Unsupported file type. Only '.json', '.txt' and '.md' files are supported."
            logger.error(error_msg)
            raise ValueError(error_msg)
    except Exception as e:
        logger.error(f"Error reading file '{file_path}': {traceback.format_exc()}")
        return None

def write_file(file_path, content, encoding='utf-8'):
    """Write content to a file based on its extension."""
    try:
        if file_path.endswith('.json'):
            with open(file_path, 'w', encoding=encoding) as file:
                json.dump(content, file, indent=4)
                
        elif file_path.endswith('.txt'):
            with open(file_path, 'w', encoding=encoding) as file:
                file.write(content)
        else:
            error_msg = "Unsupported file type. Only '.json' and '.txt' files are supported."
            logger.error(error_msg)
            raise ValueError(error_msg)
        return True
    except Exception as e:
        logger.error(f"Error writing file '{file_path}': {traceback.format_exc()}")
        return False

def replace_json_content(source_file_path, target_file_path):
    try:
        source_data = read_file(source_file_path)
        write_file(target_file_path, source_data)
    except Exception as e:
        logger.error(f"Error replacing JSON content: {e}")

def parse_datetime(datetime_str = None) -> str:
    try:
        if datetime_str is None:
            logger.error("parse_datetime: datetime_str is None")
            return None
            
        if isinstance(datetime_str, datetime):
            given_time = datetime_str
        else:
            # Handle empty or invalid strings
            if not isinstance(datetime_str, str) or not datetime_str.strip():
                logger.error(f"parse_datetime: Invalid datetime string: {datetime_str}")
                return None
                
            try:
                given_time = parser.parse(datetime_str)
            except (ValueError, TypeError) as e:
                logger.error(f"parse_datetime: Failed to parse datetime string '{datetime_str}': {e}")
                return None
            
        # Ensure the datetime has timezone info
        if given_time.tzinfo is None:
            # Assume UTC if no timezone info
            given_time = pytz.UTC.localize(given_time)
            
        given_time_utc = given_time.astimezone(pytz.UTC)
        given_time_iso_utc = given_time_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        return given_time_iso_utc
    except Exception as e:
        logger.error(f"Error parsing datetime '{datetime_str}': {e}")
        return None

def is_overlap(event, start, end):
    if isinstance(event.start, datetime) and isinstance(event.end, datetime):
        event_start = event.start.astimezone(start.tzinfo)
        event_end = event.end.astimezone(end.tzinfo)
        return event_start < end and start < event_end
    return False

def template_loader(template):
    with open(template, 'r') as file:
        return file.read()

def get_state_value(state_dict, *keys, default=None):
    current = state_dict
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current if current else default

def to_plain_text(json_input):
    """Convert JSON input to formatted text string."""
    if json_input is None:
        return ""
        
    if isinstance(json_input, str):
        if not json_input.strip():
            return ""
        try:
            data = json.loads(json_input)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON string: {str(e)}")
            return json_input  # Return the original string if JSON parsing fails
    else:
        data = json_input

    def format_value(value, indent=0):
        spacing = ' ' * indent
        
        if isinstance(value, Mapping):
            lines = []
            for k, v in value.items():
                formatted = format_value(v, indent + 2)
                if '\n' in formatted:
                    lines.append(f"{spacing}{k}:\n{formatted}")
                else:
                    lines.append(f"{spacing}{k}: {formatted}")
            return '\n'.join(lines)
            
        elif isinstance(value, (list, tuple)):
            return '\n'.join(f"{spacing}- {format_value(item, indent + 2)}" for item in value)
            
        elif isinstance(value, bool):
            return str(value).lower()
            
        elif value is None:
            return 'null'
            
        else:
            return str(value)

    return format_value(data)

def convert_to_langchain_messages(messages: List[Dict[str, Any]]) -> List[Union[HumanMessage, AIMessage, SystemMessage]]:
    result = []
    for message in messages:
        role = message.get("role", "user")

        if role == "user":
            result.append(HumanMessage(content=message["content"]))
        elif role == "assistant" or role == "ai":
            result.append(AIMessage(content=message["content"]))
        elif role == "system":
            result.append(SystemMessage(content=message["content"]))
    return result

def dict_to_xml(data, root_tag="root") -> str:
    def build_tree(parent, structure):
        if isinstance(structure, dict):
            for key, value in structure.items():
                child = ET.SubElement(parent, key)
                build_tree(child, value)
        elif isinstance(structure, list):
            for item in structure:
                child = ET.SubElement(parent, "item")
                build_tree(child, item)
        else:
            parent.text = str(structure)

    root = ET.Element(root_tag)
    build_tree(root, data)
    return ET.tostring(root, encoding='unicode', method='xml')

def to_plain_dict(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: to_plain_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_plain_dict(item) for item in obj]
    elif isinstance(obj, BaseModel):
        return to_plain_dict(obj.dict())
    else:
        return obj

# format conversation item.
def format_conversation_item(item: Dict[str, Any]) -> str:

    # Handle both ChatMessage objects and dictionaries
    if hasattr(item, 'content'):
        # ChatMessage object - access attributes directly
        content = item.content
        role = item.role
        created_at = item.created_at
    else:
        # Dictionary - access using keys
        content = item['content']
        role = item['role']
        created_at = item['created_at']
    
    # Handle content as array of strings - concatenate with spaces
    if isinstance(content, list):
        content = ' '.join(str(item) for item in content)
    else:
        content = str(content)
    
    # Check if content is a JSON string with additional data
    result = {
        "content": content,
        "role": role,
        "timestamp": datetime.fromtimestamp(created_at).strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Try to parse content as JSON and extract additional data
    if content and content.startswith('{') and content.endswith('}'):
        try:
            parsed_content = json.loads(content)
            if isinstance(parsed_content, dict):
                # Extract the actual content
                if 'content' in parsed_content:
                    result["content"] = parsed_content['content']
                
                # Add all other keys directly to the result (flattened)
                for k, v in parsed_content.items():
                    if k != 'content':
                        result[k] = v
        except json.JSONDecodeError:
            # If JSON parsing fails, keep the original content
            pass
    
    return result
    
    

def format_message(text: str) -> str:

    the_message = {
        "content": str(text),
        "role": "user",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # check if message is json
    if text and text.startswith("{") and text.endswith("}"):
        try:
            the_message = json.loads(text)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON message: {e}")
    
    return the_message

def format_conversation_history(messages: List[Union[SystemMessage, HumanMessage, AIMessage, ToolMessage]]) -> str:
    formatted_messages = []
    for message in messages:
        # Skip tool messages to avoid OpenAI API errors
        # Tool messages require proper tool_calls context which may not be available
        if isinstance(message, ToolMessage):
            continue
        elif isinstance(message, SystemMessage):
            formatted_messages.append(f"System: {message.content}")
        elif isinstance(message, HumanMessage):
            formatted_messages.append(f"Human: {message.content}")
        elif isinstance(message, AIMessage):
            formatted_messages.append(f"Assistant: {message.content}")
    return "\n".join(formatted_messages)

def convert_to_pointwise_strings(strings: List[str]) -> List[str]:
    return '\n'.join([f"• {s}" for s in strings])

# format the conversation dict to a string
def format_conversation_dict(conversation_dict: Dict[str, Any]) -> str:

    summary = ""
    # loop with each of the items in the list
    for item in conversation_dict:
        # check if the item is a human message
        summary += f"{item['type']}: {item['content']}\n"


    return summary


def load_template(template_name: str):
        prompts_path = "prompts/"
        template = read_file(f"{prompts_path}{template_name}.md")

        return template