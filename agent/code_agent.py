from create_agent import create_agent
from tools.basetool import execute_code, execute_command
from tools.FileEdit import read_document
from logger import setup_logger # Import for logging

# Initialize logger for this module if needed, or rely on LMM's logger
# For simplicity here, errors will be raised, LMM already logs failures.
# logger = setup_logger(__name__) 

def create_code_agent(language_model_manager, agent_name: str, members, working_directory):
    """Create the code agent using LanguageModelManager"""
    
    logger = setup_logger() # Get a logger instance

    actual_llm = language_model_manager.get_model(agent_name)
    
    if actual_llm is None:
        error_msg = f"Failed to retrieve LLM for agent '{agent_name}'. Agent creation aborted."
        logger.error(error_msg)
        raise ValueError(error_msg)

    tools = [read_document, execute_code, execute_command]
    system_prompt = """
    You are an expert Python programmer specializing in data processing and analysis. Your main responsibilities include:

    1. Writing clean, efficient Python code for data manipulation, cleaning, and transformation.
    2. Implementing statistical methods and machine learning algorithms as needed.
    3. Debugging and optimizing existing code for performance improvements.
    4. Adhering to PEP 8 standards and ensuring code readability with meaningful variable and function names.

    Constraints:
    - Focus solely on data processing tasks; do not generate visualizations or write non-Python code.
    - Provide only valid, executable Python code, including necessary comments for complex logic.
    - Avoid unnecessary complexity; prioritize readability and efficiency.
    """
    return create_agent(
        actual_llm, # Use the fetched LLM
        tools,
        system_prompt,
        members,
        working_directory
    )
