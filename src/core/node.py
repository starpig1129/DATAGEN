from typing import Any
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
import logging
import json
from pathlib import Path

from .state import State
from ..config import WORKING_DIRECTORY

# Set up logger
logger = logging.getLogger(__name__)

def agent_node(state: State, agent: Any, name: str) -> dict:
    """Process an agent's action and update the state accordingly."""
    logger.info(f"Processing agent: {name}")
    try:
        result = agent.invoke(state)
        
        if name == "process_agent":
            output = result["structured_response"]    
            ai_message = AIMessage(content=output.task)
        elif name == "quality_review_agent":
            output = result["structured_response"]
            ai_message = AIMessage(content=output.feedback)
        else:
            ai_message = result.get("messages")[-1]
            output = ai_message.content

        updates = {
            "messages": [ai_message],
            "sender": name
        }

        if name == "hypothesis_agent":
            updates["hypothesis"] = output
        elif name == "process_agent":
            updates["process"] = output.task
            updates["process_decision"] = output.next
        elif name == "visualization_agent":
            updates["visualization_state"] = output
        elif name == "searcher_agent":
            updates["searcher_state"] = output
        elif name == "report_agent":
            updates["report_section"] = output
        elif name == "quality_review_agent":
            updates["quality_review"] = output.feedback
            updates["needs_revision"] = output.needs_revision
        
        return updates
        
    except Exception as e:
        logger.error(f"Error in {name}: {str(e)}", exc_info=True)
        return {
            "messages": [AIMessage(content=f"Error: {str(e)}")],
            "sender": name
        }

def human_choice_node(state: State) -> dict:
    """Handle human input to choose the next step."""
    print("Please choose the next step:")
    print("1. Regenerate hypothesis")
    print("2. Continue the research process")
    
    while True:
        choice = input("Please enter your choice (1 or 2): ")
        if choice in ["1", "2"]:
            break
        print("Invalid input, please try again.")
    
    updates = {
        "messages": [HumanMessage(content="")],
        "sender": "human"
    }
    
    if choice == "1":
        modification_areas = input("Specify areas to modify: ")
        updates["messages"][0].content = f"Regenerate hypothesis. Areas: {modification_areas}"
        updates["hypothesis"] = ""  # Clear hypothesis
    else:
        updates["messages"][0].content = "Continue the research process"
        updates["process"] = "Continue the research process"
    
    return updates

def create_message(message: dict[str, Any], name: str) -> BaseMessage:
    """
    Create a BaseMessage object based on the message type.
    """
    content = message.get("content", "")
    message_type = message.get("type", "").lower()
    
    logger.debug(f"Creating message of type {message_type} for {name}")
    return HumanMessage(content=content) if message_type == "human" else AIMessage(content=content, name=name)

def note_agent_node(state: State, agent: Any, name: str) -> State:
    """
    Process the note agent's action and update the entire state.
    """
    logger.info(f"Processing note agent: {name}")
    output = ""
    try:
        current_messages = list(state.get("messages", []))
        
        head_messages: list[BaseMessage] = []
        tail_messages: list[BaseMessage] = []
        
        if len(current_messages) > 6:
            head_messages = list(current_messages[:2]) 
            tail_messages = list(current_messages[-2:])
            state = {**state, "messages": list(current_messages[2:-2])}
            logger.debug("Trimmed messages for processing")
        
        result = agent.invoke(state)
        logger.debug(f"Note agent {name} result: {result}")
        output = result["structured_response"]

        parsed_output = json.loads(output)
        logger.debug(f"Parsed output: {parsed_output}")

        new_messages = [create_message(msg, name) for msg in parsed_output.get("messages", [])]
        
        messages: list[BaseMessage] = list(new_messages) if new_messages else list(current_messages)
        
        combined_messages = head_messages + messages + tail_messages
        
        updated_state: State = {
            "messages": combined_messages,
            "hypothesis": str(parsed_output.get("hypothesis", state.get("hypothesis", ""))),
            "process": str(parsed_output.get("process", state.get("process", ""))),
            "process_decision": str(parsed_output.get("process_decision", state.get("process_decision", ""))),
            "visualization_state": str(parsed_output.get("visualization_state", state.get("visualization_state", ""))),
            "searcher_state": str(parsed_output.get("searcher_state", state.get("searcher_state", ""))),
            "code_state": str(parsed_output.get("code_state", state.get("code_state", ""))),
            "report_section": str(parsed_output.get("report_section", state.get("report_section", ""))),
            "quality_review": str(parsed_output.get("quality_review", state.get("quality_review", ""))),
            "needs_revision": bool(parsed_output.get("needs_revision", state.get("needs_revision", False))),
            "sender": 'note_agent'
        }
        
        logger.info("Updated state successfully")
        return updated_state

    except Exception as e:
        logger.error(f"Unexpected error in note_agent_node: {e}", exc_info=True)
        return _create_error_state(state, AIMessage(content=f"Unexpected error: {str(e)}", name=name), name, "Unexpected error")

def _create_error_state(state: State, error_message: AIMessage, name: str, error_type: str) -> State:
    """
    Create an error state when an exception occurs.
    """
    logger.info(f"Creating error state for {name}: {error_type}")
    error_state:State = {
            "messages": list(state.get("messages", [])) + [error_message],
            "hypothesis": str(state.get("hypothesis", "")),
            "process": str(state.get("process", "")),
            "process_decision": str(state.get("process_decision", "")),
            "visualization_state": str(state.get("visualization_state", "")),
            "searcher_state": str(state.get("searcher_state", "")),
            "code_state": str(state.get("code_state", "")),
            "report_section": str(state.get("report_section", "")),
            "quality_review": str(state.get("quality_review", "")),
            "needs_revision": bool(state.get("needs_revision", False)),
            "sender": 'note_agent'
        }
    return error_state

def human_review_node(state: State) -> dict:
    """
    Display current state to the user and update the state based on user input.
    Includes error handling for robustness.
    """
    try:
        print("Current research progress:")
        print(state)
        print("\nDo you need additional analysis or modifications?")
        
        while True:
            user_input = input("Enter 'yes' to continue analysis, or 'no' to end the research: ").lower()
            if user_input in ['yes', 'no']:
                break
            print("Invalid input. Please enter 'yes' or 'no'.")
        
        updates: dict[str, Any] = {"sender": "human"}
        
        if user_input == 'yes':
            while True:
                additional_request = input("Please enter your request: ").strip()
                if additional_request:
                    updates["messages"] = [HumanMessage(content=additional_request)]
                    updates["needs_revision"] = True
                    break
                print("Request cannot be empty.")
        else:
            updates["needs_revision"] = False
        
        return updates
        
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return {"messages": [AIMessage(content=f"Error: {str(e)}", name="human_review")]}

def refiner_node(state: State, agent: Any, name: str) -> dict:
    """
    Read MD file contents and PNG file names from the specified storage path,
    add them as report materials to a new message,
    then process with the agent and update the original state.
    If token limit is exceeded, use only MD file names instead of full content.
    """
    try:
        # Get storage path
        storage_path = Path(WORKING_DIRECTORY)
        
        # Collect materials
        materials = []
        md_files = list(storage_path.glob("*.md"))
        png_files = list(storage_path.glob("*.png"))
        
        # Process MD files
        for md_file in md_files:
            with open(md_file, "r", encoding="utf-8") as f:
                materials.append(f"MD file '{md_file.name}':\n{f.read()}")
        
        # Process PNG files
        materials.extend(f"PNG file: '{png_file.name}'" for png_file in png_files)
        
        # Combine materials
        combined_materials = "\n\n".join(materials)
        report_content = f"Report materials:\n{combined_materials}"
        
        # Create refiner state
        refiner_state = state.copy()
        refiner_state["messages"] = [HumanMessage(content=report_content)]
    
        result = agent.invoke(refiner_state)
        output = result["output"] if isinstance(result, dict) else str(result)
        
        return {
            "messages": [AIMessage(content=output, name=name)],
            "sender": name
        }
    except Exception as e:
        logger.error(f"Error in refiner_node: {str(e)}", exc_info=True)
        return {"messages": [AIMessage(content=f"Error: {str(e)}", name=name)]}
    
logger.info("Agent processing module initialized")