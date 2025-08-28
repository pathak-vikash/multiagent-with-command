from langgraph.graph import StateGraph, START, END
from .state import State
from .supervisor.nodes import supervisor
from .nodes import general, appointment, support, estimate, advisor

def create():
    workflow = StateGraph(State)
    
    workflow.add_node("supervisor", supervisor)
    workflow.add_node("general", general)
    workflow.add_node("appointment", appointment)
    workflow.add_node("support", support)
    workflow.add_node("estimate", estimate)
    workflow.add_node("advisor", advisor)
    
    workflow.add_edge(START, "supervisor")
    
    workflow.add_edge("general", END)
    workflow.add_edge("appointment", END)
    workflow.add_edge("support", END)
    workflow.add_edge("estimate", END)
    workflow.add_edge("advisor", END)
    
    return workflow.compile()

def get():
    global _main_orchestration_graph
    if _main_orchestration_graph is None:
        _main_orchestration_graph = create()
    return _main_orchestration_grap

_main_orchestration_graph = None

def reset():
    global _main_orchestration_graph
    _main_orchestration_graph = None
