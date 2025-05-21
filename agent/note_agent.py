from create_agent import create_note_agent as base_create_note_agent
from tools.FileEdit import read_document
from logger import setup_logger # Import for logging

def create_note_agent(language_model_manager, agent_name: str):
    """Create the note agent using LanguageModelManager"""

    logger = setup_logger() # Get a logger instance

    actual_llm = language_model_manager.get_model_for_agent(agent_name)

    if actual_llm is None:
        error_msg = f"Failed to retrieve LLM for agent '{agent_name}'. Agent creation aborted."
        logger.error(error_msg)
        raise ValueError(error_msg)
        
    tools = [read_document]
    system_prompt = '''
    You are a meticulous research process note-taker. Your main responsibility is to observe, summarize, and document the actions and findings of the research team. Your tasks include:

    1. Observing and recording key activities, decisions, and discussions among team members.
    2. Summarizing complex information into clear, concise, and accurate notes.
    3. Organizing notes in a structured format that ensures easy retrieval and reference.
    4. Highlighting significant insights, breakthroughs, challenges, or any deviations from the research plan.
    5. Responding only in JSON format to ensure structured documentation.

    Your output should be well-organized and easy to integrate with other project documentation.
    '''
    return base_create_note_agent(
        actual_llm, # Use the fetched LLM
        tools,
        system_prompt    
        )
