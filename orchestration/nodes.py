"""
Central nodes reference for all orchestration agents.

This module provides a centralized reference to all agent nodes
from the various sub-graphs with simplified naming.
"""

# Import all agent nodes from sub-graphs
from .general.nodes import general_agent as general
from .appointment.nodes import sop_collector as appointment
from .support.nodes import support_agent as support
from .estimate.nodes import estimate_agent as estimate
from .advisor.nodes import advisor_agent as advisor

# Export all nodes with simplified names
__all__ = [
    'general',
    'appointment',
    'support',
    'estimate',
    'advisor'
]
