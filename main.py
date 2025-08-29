#!/usr/bin/env python3
"""
Minimal main.py - just import graph and call with user input
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from orchestration.graph import get as get_graph
from orchestration.state import create as create_state
from utils.llm_helpers import initialize_langsmith
from langchain_core.messages import HumanMessage

def main():
    # Load environment
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY required")
        return
    
    # Initialize
    initialize_langsmith()
    
    # Get user input
    user_input = input("You: ").strip()
    
    # Create state with message
    state = create_state()
    state["messages"] = [HumanMessage(content=user_input)]
    
    # Call graph
    graph = get_graph()
    for chunk in graph.stream(state):
        if "messages" in chunk and len(chunk["messages"]) > 0:
            last_message = chunk["messages"][-1]
            if hasattr(last_message, 'type') and last_message.type == "ai":
                print(f"Assistant: {last_message.content}")
                break

if __name__ == "__main__":
    main()
