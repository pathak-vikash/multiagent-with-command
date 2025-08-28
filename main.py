import os
import json
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Import our centralized graph module
from graph import get_supervisor_graph, get_graph_info
from utils.llm_helpers import initialize_langsmith

def run_demo_mode():
    """Run the system in demo mode with predefined examples"""
    
    print("🚀 Initializing LangGraph Supervisor System...")
    
    # Initialize LangSmith tracing
    initialize_langsmith()
    
    supervisor_graph = get_supervisor_graph()
    print("✅ Supervisor graph created successfully!")
    
    # Display graph information
    graph_info = get_graph_info()
    print(f"📊 Graph Info: {len(graph_info['nodes'])} nodes, {graph_info['routing_method']}")
    
    # Example conversations
    example_conversations = [
        "Hi there! How are you doing today?",
        "I need to book an appointment for lawn care next Tuesday afternoon",
        "My warranty claim was denied and I'm really frustrated about it",
        "What services do you offer and what are your business hours?",
        "Can you give me a quote for cleaning services at 123 Main Street?",
        "Thanks for your help, you've been great!",
        "What's the weather like today? Just curious!"
    ]
    
    print(f"\n{'='*80}")
    print("🎯 LangGraph Multi-Agent Supervisor System - Demo Mode")
    print(f"{'='*80}")
    print("This system demonstrates intelligent routing to specialized agents:")
    print("• General Agent: Casual conversation and greetings")
    print("• Appointment Agent: Booking and scheduling")
    print("• Support Agent: Customer Support and warranty claims")
    print("• Estimate Agent: Price quotes and estimates")
    print("• Advisor Agent: Business information and recommendations")
    print(f"{'='*80}\n")
    
    # Process each example
    for i, message in enumerate(example_conversations, 1):
        print(f"\n{'='*80}")
        print(f"💬 Example {i}: User Input")
        print(f"{'='*80}")
        print(f"👤 User: {message}")
        print(f"{'='*80}")
        
        # Stream the conversation
        try:
            response_received = False
            for chunk in supervisor_graph.stream({
                "messages": [{"role": "user", "content": message}],
                "conversation_history": [],
                "context": {},
                "user_info": {},
                "session_data": {}
            }):
                # Print the response
                if "messages" in chunk and len(chunk["messages"]) > 0:
                    last_message = chunk["messages"][-1]
                    if last_message["role"] == "assistant":
                        print(f"🤖 Assistant: {last_message['content']}")
                        response_received = True
                        
                        # Print structured data if available
                        current_agent = chunk.get("current_agent")
                        if current_agent:
                            print(f"🏷️ Handled by: {current_agent}")
                        
                        # Print additional context
                        if "supervisor_decision" in chunk:
                            decision = chunk["supervisor_decision"]
                            print(f"🎯 Intent: {decision.intent_type} (confidence: {decision.confidence:.2f})")
                            print(f"💭 Reasoning: {decision.reasoning}")
                        
                        # Print agent-specific results
                        if "appointment_result" in chunk and chunk["appointment_result"]:
                            result = chunk["appointment_result"]
                            print(f"📅 Appointment ID: {result.appointment_id}")
                        
                        if "support_result" in chunk and chunk["support_result"]:
                            result = chunk["support_result"]
                            print(f"🎫 Support Ticket: {result.ticket_id}")
                        
                        if "estimate_result" in chunk and chunk["estimate_result"]:
                            result = chunk["estimate_result"]
                            print(f"💰 Estimate ID: {result.estimate_id}")
                        
                        if "advisor_result" in chunk and chunk["advisor_result"]:
                            result = chunk["advisor_result"]
                            print(f"📋 Services mentioned: {', '.join(result.services_mentioned)}")
            
            if not response_received:
                print("❌ No response generated")
            
        except Exception as e:
            print(f"❌ Error processing message: {e}")
        
        print(f"{'='*80}")
    
    print(f"\n{'='*80}")
    print("🎉 Demo completed successfully!")
    print("The system demonstrated intelligent routing and specialized agent responses.")
    print(f"{'='*80}")

def run_interactive_mode():
    """Run the system in interactive console mode"""
    
    print("🚀 Initializing LangGraph Supervisor System...")
    
    # Initialize LangSmith tracing
    initialize_langsmith()
    
    supervisor_graph = get_supervisor_graph()
    print("✅ Supervisor graph created successfully!")
    
    # Display graph information
    graph_info = get_graph_info()
    print(f"📊 Graph Info: {len(graph_info['nodes'])} nodes, {graph_info['routing_method']}")
    
    print(f"\n{'='*80}")
    print("🎯 LangGraph Multi-Agent Supervisor System - Interactive Mode")
    print(f"{'='*80}")
    print("Available agents:")
    for agent, description in graph_info["agent_types"].items():
        emoji = {
            "general_agent": "🤖",
            "appointment_agent": "📅", 
            "support_agent": "🎫",
            "estimate_agent": "💰",
            "advisor_agent": "📋"
        }.get(agent, "🤖")
        print(f"• {emoji} {agent.replace('_', ' ').title()}: {description}")
    print(f"{'='*80}")
    print("💡 Type your messages below. Type 'quit', 'exit', or 'bye' to end the session.")
    print("💡 Type 'help' for example questions.")
    print(f"{'='*80}\n")
    
    # Initialize conversation history
    conversation_history = []
    
    # Example questions for help
    help_examples = [
        "Hi there! How are you doing today?",
        "I need to book an appointment for lawn care next Tuesday afternoon",
        "My warranty claim was denied and I'm really frustrated about it",
        "What services do you offer and what are your business hours?",
        "Can you give me a quote for cleaning services at 123 Main Street?"
    ]
    
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                print("\n👋 Goodbye! Thanks for using the LangGraph Multi-Agent Supervisor System.")
                break
            
            # Check for help command
            if user_input.lower() == 'help':
                print("\n💡 Example questions you can ask:")
                for i, example in enumerate(help_examples, 1):
                    print(f"   {i}. {example}")
                print("\n💡 Or just type your own question!")
                continue
            
            # Skip empty input
            if not user_input:
                continue
            
            print("\n🤖 Assistant: ", end="", flush=True)
            
            # Process the message
            try:
                response_received = False
                for chunk in supervisor_graph.stream({
                    "messages": [{"role": "user", "content": user_input}],
                    "conversation_history": conversation_history,
                    "context": {},
                    "user_info": {},
                    "session_data": {}
                }):
                    # Print the response
                    if "messages" in chunk and len(chunk["messages"]) > 0:
                        last_message = chunk["messages"][-1]
                        if last_message["role"] == "assistant":
                            print(last_message['content'])
                            response_received = True
                            
                            # Print additional info in a compact format
                            current_agent = chunk.get("current_agent")
                            if current_agent:
                                print(f"   [Handled by: {current_agent}]")
                            
                            if "supervisor_decision" in chunk:
                                decision = chunk["supervisor_decision"]
                                print(f"   [Intent: {decision.intent_type}, Confidence: {decision.confidence:.2f}]")
                
                if not response_received:
                    print("❌ No response generated")
                
                # Update conversation history
                conversation_history.append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                print(f"❌ Error processing your message: {e}")
                print("Please try again with a different question.")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for using the LangGraph Multi-Agent Supervisor System.")
            break
        except EOFError:
            print("\n\n👋 Goodbye! Thanks for using the LangGraph Multi-Agent Supervisor System.")
            break

def main():
    """Main application with command line argument support"""
    
    # Load environment variables
    load_dotenv()
    
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable is required")
        print("Please set your OpenAI API key in the .env file")
        return
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="LangGraph Multi-Agent Supervisor System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run in interactive mode (default)
  python main.py --demo            # Run demo with predefined examples
  python main.py --interactive     # Run in interactive mode
  python main.py -h                # Show this help message
        """
    )
    
    parser.add_argument(
        '--demo', 
        action='store_true',
        help='Run in demo mode with predefined examples'
    )
    
    parser.add_argument(
        '--interactive', 
        action='store_true',
        help='Run in interactive console mode (default)'
    )
    
    args = parser.parse_args()
    
    # Determine mode
    if args.demo:
        run_demo_mode()
    else:
        # Default to interactive mode
        run_interactive_mode()

if __name__ == "__main__":
    main()
