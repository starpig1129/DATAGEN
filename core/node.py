from typing import Any
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage,ToolMessage
from openai import InternalServerError
from core.state import State
import logging
import json
import re
import os
from pathlib import Path
from langchain.agents import AgentExecutor
# Set up logger
logger = logging.getLogger(__name__)

def agent_node(state: State, agent: AgentExecutor, name: str) -> State:
    """
    Process an agent's action and update the state accordingly.
    """
    logger.info(f"Processing agent: {name}")
    try:
        result = agent.invoke(state)
        logger.debug(f"Agent {name} result: {result}")
        
        output = result["output"] if isinstance(result, dict) and "output" in result else str(result)
        
        ai_message = AIMessage(content=output, name=name)
        state["messages"].append(ai_message)
        state["sender"] = name
        
        if name == "hypothesis_agent" and not state["hypothesis"]:
            state["hypothesis"] = ai_message
            logger.info("Hypothesis updated")
        elif name == "process_agent":
            state["process_decision"] = ai_message
            logger.info("Process decision updated")
            print(f"=== process_agent輸出調試 ===")
            print(f"process_agent輸出內容: {ai_message.content}")
            print(f"設置process_decision為: {ai_message}")
            print(f"當前sender: {state.get('sender', 'None')}")
        elif name == "visualization_agent":
            state["visualization_state"] = ai_message
            logger.info("Visualization state updated")
        elif name == "searcher_agent":
            state["searcher_state"] = ai_message
            logger.info("Searcher state updated")
        elif name == "report_agent":
            state["report_section"] = ai_message
            logger.info("Report section updated")
        elif name == "quality_review_agent":
            state["quality_review"] = ai_message
            state["needs_revision"] = "revision needed" in output.lower()
            logger.info(f"Quality review updated. Needs revision: {state['needs_revision']}")
        
        logger.info(f"Agent {name} processing completed")
        return state
    except Exception as e:
        logger.error(f"Error occurred while processing agent {name}: {str(e)}", exc_info=True)
        error_message = AIMessage(content=f"Error: {str(e)}", name=name)
        return {"messages": [error_message]}

def human_choice_node(state: State) -> State:
    """
    Handle human input to choose the next step in the process.
    Supports both CMD and UI input methods.
    """
    print("=== 進入 human_choice_node ===")
    logger.info("Processing human choice")
    
    # Check if we already have a process_decision from UI (e.g., user clicked a button)
    ui_decision = state.get("process_decision")
    if ui_decision:
        choice = ui_decision # Use the decision from UI
        modification_areas = "" # No modification areas needed if continuing
        # Clear the decision immediately after reading it
        state["process_decision"] = ""
        logger.info(f"Received UI decision: {choice}")
        print(f"=== human_choice_node 處理UI決策 ===")
        print(f"UI決策值: {ui_decision}")
        print(f"決策選擇: {choice}")
    else:
        # Add prompt message for both UI and CMD if no UI decision was passed
        prompt_message = "Please choose the next step:\n1. Regenerate hypothesis\n2. Continue the research process"
        state["messages"].append(AIMessage(content=prompt_message))
        
        # 強制使用UI模式，因為我們在Web應用環境中
        # For UI - return current state and wait for input
        print("=== UI模式檢測到，設置sender為human_choice並返回狀態 ===")
        print(f"當前狀態中的消息數: {len(state.get('messages', []))}")
        state["sender"] = "human_choice"
        print(f"已設置sender為: {state['sender']}")
        return state
    
    # Process the choice
    if choice == "1":
        content = f"Regenerate hypothesis. Areas to modify: {modification_areas}"
        state["hypothesis"] = ""
        state["modification_areas"] = modification_areas
        logger.info("Hypothesis cleared for regeneration")
        logger.info(f"Areas to modify: {modification_areas}")
    else:
        content = "Continue the research process"
        state["process"] = "Continue the research process"
        logger.info("Continuing research process")
        logger.info(f"當前hypothesis狀態: {state.get('hypothesis', 'None')}")
        # 確保hypothesis_router會正確路由到Process
        print(f"=== 決策處理完成，choice={choice}, hypothesis='{state.get('hypothesis', '')}' ===")
    
    human_message = HumanMessage(content=content)
    state["messages"].append(human_message)
    state["sender"] = "human"
    # Ensure process_decision is cleared after processing any choice
    state["process_decision"] = ""

    logger.info("Human choice processed")
    return state

def create_message(message: dict[str], name: str) -> BaseMessage:
    """
    Create a BaseMessage object based on the message type.
    """
    content = message.get("content", "")
    message_type = message.get("type", "").lower()
    
    logger.debug(f"Creating message of type {message_type} for {name}")
    return HumanMessage(content=content) if message_type == "human" else AIMessage(content=content, name=name)

def note_agent_node(state: State, agent: AgentExecutor, name: str) -> State:
    """
    Process the note agent's action and update the entire state.
    """
    logger.info(f"Processing note agent: {name}")
    try:
        current_messages = state.get("messages", [])
        
        head_messages, tail_messages = [], []
        
        if len(current_messages) > 6:
            head_messages = current_messages[:2] 
            tail_messages = current_messages[-2:]
            state = {**state, "messages": current_messages[2:-2]}
            logger.debug("Trimmed messages for processing")
        
        result = agent.invoke(state)
        logger.debug(f"Note agent {name} result: {result}")
        output = result["output"] if isinstance(result, dict) and "output" in result else str(result)

        cleaned_output = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', output)
        parsed_output = json.loads(cleaned_output)
        logger.debug(f"Parsed output: {parsed_output}")

        new_messages = [create_message(msg, name) for msg in parsed_output.get("messages", [])]
        
        messages = new_messages if new_messages else current_messages
        
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

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}", exc_info=True)
        return _create_error_state(state, AIMessage(content=f"Error parsing output: {output}", name=name), name, "JSON decode error")

    except InternalServerError as e:
        logger.error(f"OpenAI Internal Server Error: {e}", exc_info=True)
        return _create_error_state(state, AIMessage(content=f"OpenAI Error: {str(e)}", name=name), name, "OpenAI error")

    except Exception as e:
        logger.error(f"Unexpected error in note_agent_node: {e}", exc_info=True)
        return _create_error_state(state, AIMessage(content=f"Unexpected error: {str(e)}", name=name), name, "Unexpected error")

def human_review_node(state: State) -> State:
    """
    Display current state and handle user input for additional analysis.
    Supports both CMD and UI input methods.
    """
    logger.info("Starting human review")
    
    # Add state review message
    review_message = "Current research progress:\n" + str(state)
    state["messages"].append(AIMessage(content=review_message))
    
    # Add prompt for both UI and CMD
    prompt_message = "\nDo you need additional analysis or modifications?"
    state["messages"].append(AIMessage(content=prompt_message))
    
    # For CMD interface
    if os.isatty(0):
        while True:
            user_input = input("Enter 'yes' to continue analysis, or 'no' to end the research: ").lower()
            if user_input in ['yes', 'no']:
                break
            print("Invalid input. Please enter 'yes' or 'no'.")
        
        if user_input == 'yes':
            while True:
                additional_request = input("Please enter your additional analysis request: ").strip()
                if additional_request:
                    state["messages"].append(HumanMessage(content=additional_request))
                    state["needs_revision"] = True
                    break
                print("Request cannot be empty. Please try again.")
        else:
            state["needs_revision"] = False
    else:
        # For UI - return current state and wait for input
        state["sender"] = "human_review"
        return state
    
    state["sender"] = "human"
    logger.info("Human review completed")
    return state
    
def refiner_node(state: State, agent: AgentExecutor, name: str) -> State:
    """
    Read MD file contents and PNG file names from the specified storage path,
    add them as report materials to a new message,
    then process with the agent and update the original state.
    If token limit is exceeded, use only MD file names instead of full content.
    """
    try:
        # Get storage path
        storage_path = Path(os.getenv('STORAGE_PATH', './data_storage/'))
        
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
        refiner_state["messages"] = [BaseMessage(content=report_content)]
        
        try:
            # Attempt to invoke agent with full content
            result = agent.invoke(refiner_state)
        except Exception as token_error:
            # If token limit is exceeded, retry with only MD file names
            logger.warning("Token limit exceeded. Retrying with MD file names only.")
            md_file_names = [f"MD file: '{md_file.name}'" for md_file in md_files]
            png_file_names = [f"PNG file: '{png_file.name}'" for png_file in png_files]
            
            simplified_materials = "\n".join(md_file_names + png_file_names)
            simplified_report_content = f"Report materials (file names only):\n{simplified_materials}"
            
            refiner_state["messages"] = [BaseMessage(content=simplified_report_content)]
            result = agent.invoke(refiner_state)
        
        # Update original state
        state["messages"].append(AIMessage(content=result))
        state["sender"] = name
        
        logger.info("Refiner node processing completed")
        return state
    except Exception as e:
        logger.error(f"Error occurred while processing refiner node: {str(e)}", exc_info=True)
        state["messages"].append(AIMessage(content=f"Error: {str(e)}", name=name))
        return state
    
def _create_error_state(state: State, error_message: AIMessage, name: str, error_type: str) -> State:
    """
    Create an error state when an exception occurs.
    """
    logger.info(f"Creating error state for {name}: {error_type}")
    error_state:State = {
            "messages": state.get("messages", []) + [error_message],
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
    
logger.info("Agent processing module initialized")
