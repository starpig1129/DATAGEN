from create_agent import create_agent
from tools.FileEdit import create_document, read_document, edit_document
from logger import setup_logger # Import for logging

def create_quality_review_agent(language_model_manager, agent_name: str, members, working_directory):
    """Create the quality review agent using LanguageModelManager"""

    logger = setup_logger() # Get a logger instance

    actual_llm = language_model_manager.get_model_for_agent(agent_name)

    if actual_llm is None:
        error_msg = f"Failed to retrieve LLM for agent '{agent_name}'. Agent creation aborted."
        logger.error(error_msg)
        raise ValueError(error_msg)

    tools = [create_document, read_document, edit_document]
    system_prompt = '''
    You are a meticulous quality control expert responsible for reviewing and ensuring the high standard of all research outputs. Your tasks include:

    1. Critically evaluating the content, methodology, and conclusions of research reports.
    2. Checking for consistency, accuracy, and clarity in all documents.
    3. Identifying areas that need improvement or further elaboration.
    4. Ensuring adherence to scientific writing standards and ethical guidelines.

    After your review, if revisions are needed, respond with 'REVISION' as a prefix, set needs_revision=True, and provide specific feedback on parts that need improvement. If no revisions are necessary, respond with 'CONTINUE' as a prefix and set needs_revision=False.
    '''
    return create_agent(
        actual_llm, # Use the fetched LLM
        tools,
        system_prompt,
        members,
        working_directory
    )
