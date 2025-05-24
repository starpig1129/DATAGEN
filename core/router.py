from core.state import State
from typing import Literal, Union, Dict, List, Optional
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
    hypothesis: Union[AIMessage, str, None] = state.get("hypothesis")
    
    # 添加詳細的調試信息
    print(f"=== hypothesis_router 調試 ===")
    print(f"原始hypothesis值: {repr(hypothesis)}")
    print(f"hypothesis類型: {type(hypothesis)}")
    print(f"state中的process: {state.get('process', 'None')}")
    print(f"state中的sender: {state.get('sender', 'None')}")
    
    try:
        if isinstance(hypothesis, AIMessage):
            hypothesis_content = hypothesis.content
            logger.debug("Hypothesis is an AIMessage")
        elif isinstance(hypothesis, str):
            hypothesis_content = hypothesis
            logger.debug("Hypothesis is a string")
        else:
            hypothesis_content = ""
            logger.warning(f"Unexpected hypothesis type: {type(hypothesis)}")
            
        if not isinstance(hypothesis_content, str):
            hypothesis_content = str(hypothesis_content)
            logger.warning("Converting hypothesis content to string")
    except Exception as e:
        logger.error(f"Error processing hypothesis: {e}")
        hypothesis_content = ""
    
    print(f"處理後的hypothesis_content: '{hypothesis_content}'")
    print(f"hypothesis_content.strip(): '{hypothesis_content.strip()}'")
    print(f"not hypothesis_content.strip(): {not hypothesis_content.strip()}")
    
    result = "Hypothesis" if not hypothesis_content.strip() else "Process"
    logger.info(f"hypothesis_router decision: {result}")
    print(f"=== hypothesis_router 決策: {result} ===")
    return result

def QualityReview_router(state: State) -> NodeType:
    """
    Route based on the quality review outcome and process decision.

    Args:
    state (State): The current state of the system.

    Returns:
    NodeType: The next node to route to based on the quality review and process decision.
    """
    logger.info("Entering QualityReview_router")
    messages = state.get("messages", [])
    last_message = messages[-1] if messages else None
    
    # Check if revision is needed
    if (last_message and 'REVISION' in str(last_message.content)) or state.get("needs_revision", False):
        previous_node = state.get("last_sender", "")
        revision_routes = {
            "Visualization": "Visualization",
            "Search": "Search",
            "Coder": "Coder",
            "Report": "Report"
        }
        result = revision_routes.get(previous_node, "NoteTaker")
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
    process_decision: Union[AIMessage, Dict, str, None] = state.get("process_decision", "")
    
    # 添加詳細的調試信息
    print(f"=== process_router 調試 ===")
    print(f"原始process_decision值: {repr(process_decision)}")
    print(f"process_decision類型: {type(process_decision)}")
    print(f"state中的sender: {state.get('sender', 'None')}")
    
    decision_str: str = ""
    
    try:
        if isinstance(process_decision, AIMessage):
            logger.debug("Process decision is an AIMessage")
            try:
                decision_dict = json.loads(process_decision.content.replace("'", '"'))
                decision_str = str(decision_dict.get('next', ''))
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse error: {e}. Using content directly.")
                decision_str = process_decision.content
        elif isinstance(process_decision, dict):
            decision_str = str(process_decision.get('next', ''))
        else:
            decision_str = str(process_decision)
    except Exception as e:
        logger.error(f"Error processing decision: {e}")
        decision_str = ""
    
    # Define valid decisions
    valid_decisions = {"Coder", "Search", "Visualization", "Report"}
    
    if decision_str in valid_decisions:
        logger.info(f"Valid process decision: {decision_str}")
        return decision_str
    
    if decision_str == "FINISH":
        logger.info("Process decision is FINISH. Ending process.")
        return "Refiner"
    
    # If decision_str is empty or not a valid decision, return "Process"
    if not decision_str or decision_str not in valid_decisions:
        logger.warning(f"Invalid or empty process decision: {decision_str}. Defaulting to 'Process'.")
        print(f"=== process_router 決策: Process (invalid/empty) ===")
        return "Process"
    
    # Default to "Process"
    logger.info("Defaulting to 'Process'")
    print(f"=== process_router 決策: Process (default) ===")
    return "Process"

logger.info("Router module initialized")
