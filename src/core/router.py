from .state import State
from typing import Literal, Union, Dict, List, Optional, cast
from langchain_core.messages import AIMessage
import logging
import json

# Set up logger
logger = logging.getLogger(__name__)

# Define types for node routing
NodeType = Literal['Visualization', 'Search', 'Coder', 'Report', 'Process', 'NoteTaker', 'Hypothesis', 'QualityReview']
ProcessNodeType = Literal['Coder', 'Search', 'Visualization', 'Report', 'Process', 'Refiner']

def hypothesis_router(state: State) -> NodeType:
    """
    Route based on the presence of a hypothesis in the state.

    Args:
        state (State): The current state of the system.

    Returns:
        NodeType: 'Hypothesis' if no hypothesis exists, otherwise 'Process'.
    """
    logger.info("Entering hypothesis_router")
    if state.get("process") == "Continue the research process":
        return "Process"
    else:
        return "Hypothesis"

def QualityReview_router(state: State) -> str:
    """
    Route based on the quality review outcome and process decision.

    Args:
    state (State): The current state of the system.

    Returns:
    NodeType: The next node to route to based on the quality review and process decision.
    """
    logger.info("Entering QualityReview_router")
    messages = state.get("messages", [])
    
    # Check if revision is needed
    if state.get("needs_revision", False):
        previous_node = messages[-2].name if len(messages) >= 2 else "NoteTaker"
        revision_routes = {
            "visualization_agent": "Visualization",
            "searcher_agent": "Search",
            "code_agent": "Coder",
            "report_agent": "Report"
        }
        result = revision_routes.get((str(previous_node)), "NoteTaker")
        logger.info(f"Revision needed. Routing to: {result}")
        return result
    
    else:
        return "NoteTaker"
    

def process_router(state: State) -> ProcessNodeType:
    """
    Route based on the process decision in the state.

    Args:
        state (State): The current state of the system.

    Returns:
        ProcessNodeType: The next process node to route to based on the process decision.
    """
    logger.info("Entering process_router")
    process_decision = state.get("process_decision", "")
    
    valid_decisions = {"Coder", "Search", "Visualization", "Report"}
    
    if process_decision in valid_decisions:
        return cast(ProcessNodeType, process_decision)
    
    if process_decision == "FINISH":
        return "Refiner"
    
    logger.warning(f"Invalid decision: {process_decision}. Defaulting to 'Process'.")
    return "Process"

logger.info("Router module initialized")
