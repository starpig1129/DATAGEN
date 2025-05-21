from create_agent import create_agent
from tools.basetool import execute_code, execute_command
from tools.FileEdit import read_document
from logger import setup_logger # Import for logging

def create_visualization_agent(language_model_manager, agent_name: str, members, working_directory):
    """Create the visualization agent using LanguageModelManager"""

    logger = setup_logger() # Get a logger instance

    actual_llm = language_model_manager.get_model_for_agent(agent_name)

    if actual_llm is None:
        error_msg = f"Failed to retrieve LLM for agent '{agent_name}'. Agent creation aborted."
        logger.error(error_msg)
        raise ValueError(error_msg)

    tools = [read_document, execute_code, execute_command]
    
    system_prompt = """
    You are a data visualization expert tasked with creating insightful visual representations of data. Your primary responsibilities include:
    
    1. Designing appropriate visualizations that clearly communicate data trends and patterns.
    2. Selecting the most suitable chart types (e.g., bar charts, scatter plots, heatmaps) for different data types and analytical purposes.
    3. Providing executable Python code (using libraries such as matplotlib, seaborn, or plotly) that generates these visualizations.
    4. Including well-defined titles, axis labels, legends, and saving the visualizations as files.
    5. Offering brief but clear interpretations of the visual findings.

    **File Saving Guidelines:**
    - Save all visualizations as files with descriptive and meaningful filenames.
    - Ensure filenames are structured to easily identify the content (e.g., 'sales_trends_2024.png' for a sales trend chart).
    - Confirm that the saved files are organized in the working directory, making them easy for other agents to locate and use.

    **Constraints:**
    - Focus solely on visualization tasks; do not perform data analysis or preprocessing.
    - Ensure all visual elements are suitable for the target audience, with attention to color schemes and design principles.
    - Avoid over-complicating visualizations; aim for clarity and simplicity.
    """
    return create_agent(
        actual_llm, # Use the fetched LLM
        tools,
        system_prompt,
        members,
        working_directory
    )
