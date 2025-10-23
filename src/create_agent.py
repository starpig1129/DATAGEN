from langchain.agents import create_agent
from langchain.tools import tool
import os
from .logger import setup_logger

logger = setup_logger()

def _list_directory_contents(directory: str = './data_storage/') -> str:
    """
    List the contents of the specified directory.
    
    Args:
        directory (str): The path to the directory to list. Defaults to the data storage directory.
    
    Returns:
        str: A string representation of the directory contents.
    """
    try:
        logger.info(f"Listing contents of directory: {directory}")
        contents = os.listdir(directory)
        logger.debug(f"Directory contents: {contents}")
        return f"Directory contents:\n" + "\n".join(contents)
    except Exception as e:
        logger.error(f"Error listing directory contents: {str(e)}")
        return f"Error listing directory contents: {str(e)}"
@tool
def list_directory_contents(directory: str = './data_storage/') -> str:
    """List the contents of the specified directory."""
    return _list_directory_contents(directory)

def create_base_agent(
    model,
    tools: list,
    role_prompt: str,
    team_members: list[str],
    working_directory: str = './data_storage/'
):
    """Create an agent with the given parameters."""
    
    logger.info("Creating agent")

    # Ensure the ListDirectoryContents tool is available
    if list_directory_contents not in tools:
        tools.append(list_directory_contents)

    # Prepare system prompt
    tool_names = ", ".join([tool.name for tool in tools])
    team_members_str = ", ".join(team_members)
    initial_directory_contents = _list_directory_contents(working_directory)

    system_prompt = (
        "You are a specialized AI assistant in a data analysis team. "
        "Your role is to complete specific tasks in the research process. "
        "Use the provided tools to make progress on your task. "
        "If you can't fully complete a task, explain what you've done and what's needed next. "
        "Always aim for accurate and clear outputs. "
        f"You have access to the following tools: {tool_names}. "
        f"Your specific role: {role_prompt}\n"
        "Work autonomously according to your specialty, using the tools available to you. "
        "Do not ask for clarification. "
        "Your other team members (and other teams) will collaborate with you based on their specialties. "
        f"You are chosen for a reason! You are one of the following team members: {team_members_str}.\n"
        f"The initial contents of your working directory are:\n{initial_directory_contents}\n"
        "Use the ListDirectoryContents tool to check for updates in the directory contents when needed."
    )

    # Create agent
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt
    )
    
    logger.info("Agent created successfully")
    return agent