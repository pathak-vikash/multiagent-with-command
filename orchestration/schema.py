from enum import Enum

# All nodes in the orchestration graph
class Node(Enum):
    START = "start"
    ROUTER = "router"
    SUPPORT = "support"
    APPOINTMENT = "appointment"
    ESTIMATE = "estimate"
    ADVISOR = "advisor"
    GENERAL = "general"