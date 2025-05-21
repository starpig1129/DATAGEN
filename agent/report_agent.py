from create_agent import create_agent
from tools.FileEdit import create_document, read_document, edit_document
from logger import setup_logger # Import for logging

def create_report_agent(language_model_manager, agent_name: str, members, working_directory):
    """Create the report agent using LanguageModelManager"""

    logger = setup_logger() # Get a logger instance

    actual_llm = language_model_manager.get_model_for_agent(agent_name)

    if actual_llm is None:
        error_msg = f"Failed to retrieve LLM for agent '{agent_name}'. Agent creation aborted."
        logger.error(error_msg)
        raise ValueError(error_msg)

    tools = [create_document, read_document, edit_document]
    
    system_prompt = """
    You are an experienced scientific writer tasked with drafting comprehensive research reports. Your primary duties include:

    1. Clearly stating the research hypothesis and objectives in the introduction.
    2. Detailing the methodology used, including data collection and analysis techniques.
    3. Structuring the report into coherent sections (e.g., Introduction, Methodology, Results, Discussion, Conclusion).
    4. Synthesizing information from various sources into a unified narrative.
    5. Integrating relevant data visualizations and ensuring they are appropriately referenced and explained.

    Constraints:
    - Focus solely on report writing; do not perform data analysis or create visualizations.
    - Maintain an objective, academic tone throughout the report.
    - Cite all sources using APA style and ensure that all findings are supported by evidence.
    """
    return create_agent(
        actual_llm, # Use the fetched LLM
        tools,
        system_prompt,
        members,
        working_directory
    )
