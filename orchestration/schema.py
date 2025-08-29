from enum import Enum

# All nodes in the orchestration graph
class Node(Enum):
    START = "start"
    SUPPORT = "support"
    APPOINTMENT = "appointment"
    ESTIMATE = "estimate"
    ADVISOR = "advisor"
    GENERAL = "general"
    SUPERVISOR = "supervisor"