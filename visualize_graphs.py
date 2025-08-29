#!/usr/bin/env python3
"""
Graph Visualization Command Line Tool

This script provides a command-line interface to visualize LangGraph graphs
in the orchestration system.

Usage:
    python visualize_graphs.py [graph_name] [options]

Examples:
    python visualize_graphs.py appointment
    python visualize_graphs.py main
    python visualize_graphs.py all --mermaid --config
    python visualize_graphs.py --list
"""

import sys
import os
import argparse
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.graph_visualizer import visualize_graph, save_graph_visualization

# Available graphs mapping
AVAILABLE_GRAPHS = {
    "appointment": {
        "module": "orchestration.appointment.graph",
        "function": "get",
        "name": "Appointment Sub-Graph"
    },
    "main": {
        "module": "orchestration.graph", 
        "function": "get",
        "name": "Main Orchestration Graph"
    },
    "general": {
        "module": "orchestration.general.graph",
        "function": "get", 
        "name": "General Agent Sub-Graph"
    },
    "support": {
        "module": "orchestration.support.graph",
        "function": "get",
        "name": "Support Agent Sub-Graph"
    },
    "estimate": {
        "module": "orchestration.estimate.graph", 
        "function": "get",
        "name": "Estimate Agent Sub-Graph"
    },
    "advisor": {
        "module": "orchestration.advisor.graph",
        "function": "get",
        "name": "Advisor Agent Sub-Graph"
    }
}

def get_graph(graph_name: str) -> Any:
    """
    Get a graph by name.
    
    Args:
        graph_name: Name of the graph to retrieve
        
    Returns:
        The graph object
        
    Raises:
        ImportError: If the graph module cannot be imported
        AttributeError: If the graph function is not found
    """
    if graph_name not in AVAILABLE_GRAPHS:
        raise ValueError(f"Unknown graph: {graph_name}. Available graphs: {list(AVAILABLE_GRAPHS.keys())}")
    
    graph_info = AVAILABLE_GRAPHS[graph_name]
    
    # Import the module
    module = __import__(graph_info["module"], fromlist=[graph_info["function"]])
    
    # Get the function
    get_function = getattr(module, graph_info["function"])
    
    # Return the graph
    return get_function()

def list_available_graphs():
    """List all available graphs."""
    print("Available graphs:")
    print("=" * 30)
    for name, info in AVAILABLE_GRAPHS.items():
        print(f"  {name}: {info['name']}")
    print()

def visualize_single_graph(graph_name: str, include_mermaid: bool = True, 
                          include_config: bool = False, save_files: bool = False):
    """Visualize a single graph."""
    try:
        print(f"Visualizing {graph_name} graph...")
        print("=" * 50)
        
        graph = get_graph(graph_name)
        graph_info = AVAILABLE_GRAPHS[graph_name]
        
        if save_files:
            save_graph_visualization(graph, graph_info["name"])
        else:
            visualize_graph(graph, graph_info["name"], 
                          include_mermaid=include_mermaid, 
                          include_config=include_config)
        
        print(f"✅ Successfully visualized {graph_name} graph")
        
    except Exception as e:
        print(f"❌ Error visualizing {graph_name} graph: {e}")
        import traceback
        traceback.print_exc()

def visualize_all_graphs(include_mermaid: bool = True, include_config: bool = False, 
                        save_files: bool = False):
    """Visualize all available graphs."""
    print("Visualizing all graphs...")
    print("=" * 50)
    
    for graph_name in AVAILABLE_GRAPHS.keys():
        try:
            visualize_single_graph(graph_name, include_mermaid, include_config, save_files)
            print()  # Add spacing between graphs
        except Exception as e:
            print(f"❌ Failed to visualize {graph_name}: {e}")
            print()

def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="Visualize LangGraph graphs in the orchestration system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python visualize_graphs.py appointment
  python visualize_graphs.py main --mermaid --config
  python visualize_graphs.py all --save
  python visualize_graphs.py --list
        """
    )
    
    parser.add_argument(
        "graph_name", 
        nargs="?", 
        help="Name of the graph to visualize (or 'all' for all graphs)"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all available graphs"
    )
    
    parser.add_argument(
        "--mermaid", "-m",
        action="store_true",
        default=True,
        help="Include Mermaid diagram (default: True)"
    )
    
    parser.add_argument(
        "--config", "-c",
        action="store_true",
        help="Include JSON configuration"
    )
    
    parser.add_argument(
        "--save", "-s",
        action="store_true",
        help="Save visualization files to disk"
    )
    
    parser.add_argument(
        "--no-mermaid",
        action="store_true",
        help="Disable Mermaid diagram generation"
    )
    
    args = parser.parse_args()
    
    # Handle --list option
    if args.list:
        list_available_graphs()
        return
    
    # Handle no graph name
    if not args.graph_name:
        print("Error: Please specify a graph name or use --list to see available graphs")
        parser.print_help()
        return
    
    # Handle --no-mermaid
    if args.no_mermaid:
        args.mermaid = False
    
    # Visualize graphs
    if args.graph_name.lower() == "all":
        visualize_all_graphs(args.mermaid, args.config, args.save)
    else:
        visualize_single_graph(args.graph_name, args.mermaid, args.config, args.save)

if __name__ == "__main__":
    main()
