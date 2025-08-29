from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from .state import State
from .supervisor.nodes import supervisor
from .nodes import general, appointment, support, estimate, advisor, start
from .schema import Node

def create():
    workflow = StateGraph(State)
    
    workflow.add_node(Node.START.value, start)
    #workflow.add_node(Node.SUPERVISOR.value, supervisor)
    #workflow.add_node(Node.GENERAL.value, general)
    workflow.add_node(Node.APPOINTMENT.value, appointment)
    #workflow.add_node(Node.SUPPORT.value, support)
    #workflow.add_node(Node.ESTIMATE.value, estimate)
    #workflow.add_node(Node.ADVISOR.value, advisor)
    
    #workflow.add_edge(START, Node.SUPERVISOR.value)
    workflow.add_edge(START, Node.START.value)
    #`workflow.add_edge(Node.GENERAL.value, END)

    workflow.add_edge(Node.APPOINTMENT.value, END)
    #workflow.add_edge(Node.SUPPORT.value, END)
    #workflow.add_edge(Node.ESTIMATE.value, END)
    #workflow.add_edge(Node.ADVISOR.value, END)
    
    #memory = MemorySaver()
    return workflow.compile()

def get():
    global _main_orchestration_graph
    if _main_orchestration_graph is None:
        _main_orchestration_graph = create()
    return _main_orchestration_graph

_main_orchestration_graph = None

def reset():
    global _main_orchestration_graph
    _main_orchestration_graph = None

# print graph
if __name__ == "__main__":
    from utils.graph_visualizer import visualize_graph
    
    graph = get()
    visualize_graph(graph, "Main Orchestration Graph", include_mermaid=True, include_config=True)
