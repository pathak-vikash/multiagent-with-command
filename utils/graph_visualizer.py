"""
Graph Visualization Utilities for LangGraph

This module provides utilities to visualize and print LangGraph graphs
in various formats including Mermaid diagrams, JSON configuration, and text summaries.
"""

import json
from typing import Any, Dict, Optional
from core.logger import logger


def print_graph_info(graph: Any, graph_name: str = "Graph") -> None:
    """
    Print comprehensive information about a LangGraph graph.
    
    Args:
        graph: The compiled LangGraph graph object
        graph_name: Name of the graph for display purposes
    """
    print(f"=== {graph_name} Visualization ===\n")
    
    # Print basic graph structure
    print("1. Graph Structure:")
    print(f"   - Graph Type: {type(graph).__name__}")
    
    # Handle different graph types
    if hasattr(graph, 'state_type'):
        print(f"   - State Type: {graph.state_type}")
    elif hasattr(graph, 'get_graph'):
        graph_obj = graph.get_graph()
        if hasattr(graph_obj, 'state_type'):
            print(f"   - State Type: {graph_obj.state_type}")
        else:
            print(f"   - State Type: Unknown (compiled graph)")
    else:
        print(f"   - State Type: Unknown")
    
    print(f"   - Compiled: {hasattr(graph, 'get_graph')}")
    print()
    
    if not hasattr(graph, 'get_graph'):
        print("Graph is not compiled or doesn't support visualization methods.")
        return
    
    graph_obj = graph.get_graph()
    
    # Print nodes
    print("2. Nodes:")
    if hasattr(graph_obj, 'nodes'):
        for node_name in graph_obj.nodes:
            print(f"   - {node_name}")
    else:
        print("   - No nodes information available")
    print()
    
    # Print edges
    print("3. Edges:")
    if hasattr(graph_obj, 'edges'):
        for edge in graph_obj.edges:
            print(f"   - {edge}")
    else:
        print("   - No edges information available")
    print()
    
    # Print conditional edges
    print("4. Conditional Edges:")
    try:
        if hasattr(graph_obj, 'conditional_edges'):
            for node, conditions in graph_obj.conditional_edges.items():
                print(f"   - {node}:")
                for condition, target in conditions.items():
                    print(f"     {condition} -> {target}")
        else:
            print("   - No conditional edges information available")
    except Exception as e:
        print(f"   Could not get conditional edges: {e}")
    print()


def print_mermaid_diagram(graph: Any, graph_name: str = "Graph") -> None:
    """
    Print the Mermaid diagram representation of a graph.
    
    Args:
        graph: The compiled LangGraph graph object
        graph_name: Name of the graph for display purposes
    """
    if not hasattr(graph, 'get_graph'):
        print(f"Graph {graph_name} is not compiled or doesn't support Mermaid visualization.")
        return
    
    try:
        graph_obj = graph.get_graph()
        mermaid_diagram = graph_obj.draw_mermaid()
        
        print(f"=== {graph_name} Mermaid Diagram ===")
        print(mermaid_diagram)
        print()
        
        # Also save to file for easy copying
        filename = f"{graph_name.lower().replace(' ', '_')}_mermaid.md"
        with open(filename, 'w') as f:
            f.write(f"# {graph_name} Mermaid Diagram\n\n")
            f.write("```mermaid\n")
            f.write(mermaid_diagram)
            f.write("\n```\n")
        
        print(f"Mermaid diagram saved to: {filename}")
        print()
        
    except Exception as e:
        logger.error(f"Could not generate Mermaid diagram for {graph_name}: {e}")
        print(f"Could not generate Mermaid diagram: {e}")


def print_graph_config(graph: Any, graph_name: str = "Graph") -> None:
    """
    Print the JSON configuration of a graph.
    
    Args:
        graph: The compiled LangGraph graph object
        graph_name: Name of the graph for display purposes
    """
    if not hasattr(graph, 'get_graph'):
        print(f"Graph {graph_name} is not compiled or doesn't support configuration export.")
        return
    
    try:
        graph_obj = graph.get_graph()
        config = graph_obj.get_config()
        
        print(f"=== {graph_name} Configuration ===")
        print(json.dumps(config, indent=2))
        print()
        
        # Also save to file
        filename = f"{graph_name.lower().replace(' ', '_')}_config.json"
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"Configuration saved to: {filename}")
        print()
        
    except Exception as e:
        logger.error(f"Could not get graph configuration for {graph_name}: {e}")
        print(f"Could not get graph configuration: {e}")


def visualize_graph(graph: Any, graph_name: str = "Graph", 
                   include_mermaid: bool = True, 
                   include_config: bool = False) -> None:
    """
    Comprehensive graph visualization with multiple output formats.
    
    Args:
        graph: The compiled LangGraph graph object
        graph_name: Name of the graph for display purposes
        include_mermaid: Whether to include Mermaid diagram
        include_config: Whether to include JSON configuration
    """
    print_graph_info(graph, graph_name)
    
    if include_mermaid:
        print_mermaid_diagram(graph, graph_name)
    
    if include_config:
        print_graph_config(graph, graph_name)


def save_graph_visualization(graph: Any, graph_name: str = "Graph", 
                           output_dir: str = "graph_visualizations") -> None:
    """
    Save graph visualization to files in a dedicated directory.
    
    Args:
        graph: The compiled LangGraph graph object
        graph_name: Name of the graph for display purposes
        output_dir: Directory to save visualization files
    """
    import os
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save Mermaid diagram
    if hasattr(graph, 'get_graph'):
        try:
            graph_obj = graph.get_graph()
            mermaid_diagram = graph_obj.draw_mermaid()
            
            mermaid_file = os.path.join(output_dir, f"{graph_name.lower().replace(' ', '_')}_mermaid.md")
            with open(mermaid_file, 'w') as f:
                f.write(f"# {graph_name} Mermaid Diagram\n\n")
                f.write("```mermaid\n")
                f.write(mermaid_diagram)
                f.write("\n```\n")
            
            print(f"Mermaid diagram saved to: {mermaid_file}")
            
        except Exception as e:
            logger.error(f"Could not save Mermaid diagram: {e}")
    
    # Save configuration
    if hasattr(graph, 'get_graph'):
        try:
            graph_obj = graph.get_graph()
            config = graph_obj.get_config()
            
            config_file = os.path.join(output_dir, f"{graph_name.lower().replace(' ', '_')}_config.json")
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"Configuration saved to: {config_file}")
            
        except Exception as e:
            logger.error(f"Could not save configuration: {e}")
