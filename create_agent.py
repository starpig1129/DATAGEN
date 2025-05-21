from langchain.agents import create_openai_functions_agent, AgentExecutor, create_tool_calling_agent # Added create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda # Added RunnableLambda
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI # Added Google
from langchain_community.chat_models import ChatOllama # Added Ollama
from typing import List, Union, Literal
from pydantic import BaseModel, Field
from langchain.tools import tool
import os
from logger import setup_logger

# Set up logger
logger = setup_logger()

@tool
def list_directory_contents(directory: str = './data_storage/') -> str:
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
        return f"Directory contents :\n" + "\n".join(contents)
    except Exception as e:
        logger.error(f"Error listing directory contents: {str(e)}")
        return f"Error listing directory contents: {str(e)}"

def create_agent(
    llm: Union[ChatOpenAI, ChatAnthropic, ChatGoogleGenerativeAI, ChatOllama], # Expanded type hint
    tools: list[tool],
    system_message: str,
    team_members: list[str],
    working_directory: str = './data_storage/'
) -> AgentExecutor:
    """
    Create an agent with the given language model, tools, system message, and team members.
    
    Parameters:
        llm (Union[ChatOpenAI, ChatAnthropic, ChatGoogleGenerativeAI, ChatOllama]): The language model to use.
        tools (list[tool]): A list of tools the agent can use.
        system_message (str): A message defining the agent's role and tasks.
        team_members (list[str]): A list of team member roles for collaboration.
        working_directory (str): The directory where the agent's data will be stored.
        
    Returns:
        AgentExecutor: An executor that manages the agent's task execution.
    """
    
    logger.info(f"Creating agent with model type: {type(llm)}") # Log model type

    # Ensure the ListDirectoryContents tool is available
    if list_directory_contents not in tools:
        tools.append(list_directory_contents)

    # Prepare the tool names and team members for the system prompt
    tool_names = ", ".join([tool.name for tool in tools])
    team_members_str = ", ".join(team_members)

    # List the initial contents of the working directory
    initial_directory_contents = list_directory_contents(working_directory)

    # Create the system prompt for the agent
    system_prompt = (
        "You are a specialized AI assistant in a data analysis team. "
        "Your role is to complete specific tasks in the research process. "
        "Use the provided tools to make progress on your task. "
        "If you can't fully complete a task, explain what you've done and what's needed next. "
        "Always aim for accurate and clear outputs. "
        f"You have access to the following tools: {tool_names}. "
        f"Your specific role: {system_message}\n"
        "Work autonomously according to your specialty, using the tools available to you. "
        "Do not ask for clarification. "
        "Your other team members (and other teams) will collaborate with you based on their specialties. "
        f"You are chosen for a reason! You are one of the following team members: {team_members_str}.\n"
        f"The initial contents of your working directory are:\n{initial_directory_contents}\n"
        "Use the ListDirectoryContents tool to check for updates in the directory contents when needed."
    )

    # Define the prompt structure with placeholders for dynamic content
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        ("ai", "hypothesis: {hypothesis}"),
        ("ai", "process: {process}"),
        ("ai", "process_decision: {process_decision}"),
        ("ai", "visualization_state: {visualization_state}"),
        ("ai", "searcher_state: {searcher_state}"),
        ("ai", "code_state: {code_state}"),
        ("ai", "report_section: {report_section}"),
        ("ai", "quality_review: {quality_review}"),
        ("ai", "needs_revision: {needs_revision}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Use the generic tool calling agent creator, compatible with OpenAI, Anthropic, Google, and potentially Ollama models supporting tool calls
    logger.info(f"Using create_tool_calling_agent for model type: {type(llm)}")
    agent = create_tool_calling_agent(llm, tools, prompt)

    logger.info("Agent runnable created successfully")


    # Return an executor to manage the agent's task execution
    return AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=False)


def create_supervisor(
    llm: Union[ChatOpenAI, ChatAnthropic, ChatGoogleGenerativeAI, ChatOllama], # Expanded type hint
    system_prompt: str,
    members: list[str]
) -> AgentExecutor:
    # Log the start of supervisor creation
    logger.info("Creating supervisor")
    
    # Define options for routing, including FINISH and team members
    options = ["FINISH"] + members
    # Dynamically create Literal type for route options validation
    RouteOptions = Literal[tuple(options)]

    # Define Pydantic schema for routing decisions
    class RouteSchema(BaseModel):
        """Schema for routing decisions."""
        next: RouteOptions = Field(description=f"The next agent to route to or 'FINISH'. Must be one of {options}")
        task: str = Field(description="The task description for the next agent")

    # Create Pydantic output parser based on the schema
    parser = PydanticOutputParser(pydantic_object=RouteSchema)
    # Get format instructions to guide the LLM
    format_instructions = parser.get_format_instructions()

    # Define the function definition (useful for bind_tools context, using Pydantic schema)
    function_def = {
        "name": "route",
        "description": "Select the next role and assign a task based on the conversation.",
        "parameters": RouteSchema.model_json_schema() # Use Pydantic schema for parameters definition
    }

    # Create the prompt template, incorporating format instructions
    prompt = ChatPromptTemplate.from_messages(
        [
            # Use a placeholder for format instructions in the system prompt
            ("system", system_prompt + "\n\n{format_instructions_placeholder}"),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                "Given the conversation above, who should act next? "
                "Or should we FINISH? Select one of: {options}. "
                "Additionally, specify the task that the selected role should perform. "
                # Reinforce the need for the specified JSON format
                "Respond using the required JSON format."
            ),
        ]
    # Pass format_instructions via partial to avoid template variable issues
    ).partial(
        options=str(options),
        team_members=", ".join(members),
        format_instructions_placeholder=format_instructions
    )

    # Log successful creation of supervisor components
    logger.info("Supervisor prompt and parser created successfully")

    # Bind the tool/function call based on the LLM type
    if isinstance(llm, ChatOpenAI):
        logger.info("Binding function call for OpenAI model using bind_functions")
        # Force OpenAI model to call the 'route' function using standard format
        bound_llm = llm.bind_functions(functions=[function_def], function_call={"name": "route"})
    elif isinstance(llm, (ChatGoogleGenerativeAI, ChatAnthropic, ChatOllama)):
        logger.info(f"Binding tool for {type(llm).__name__} model using bind_tools (without forcing tool_choice)")
        # Bind the tool definition to provide context to Gemini/Anthropic/Ollama,
        # but rely on the prompt and Pydantic parser for structuring the output,
        # rather than forcing the call with tool_choice.
        bound_llm = llm.bind_tools(tools=[function_def])
    else:
        logger.warning(f"Unsupported LLM type for specific tool binding: {type(llm)}. Supervisor will rely solely on prompt.")
        # Fallback for unsupported models: use the LLM without specific binding.
        bound_llm = llm

    # Define a function to log the formatted prompt before sending to LLM
    def log_formatted_prompt(prompt_value):
        """Logs the fully formatted prompt value before it hits the LLM."""
        logger.info(f"Formatted prompt sent to LLM: {prompt_value.to_string()}") # Log the string representation
        # You might want to log specific parts too, e.g., messages:
        # logger.debug(f"Messages in formatted prompt: {prompt_value.to_messages()}")
        return prompt_value # Pass the prompt value along the chain

    # Define a function to log the LLM output before parsing
    def log_llm_output(input_data):
        """Logs the raw output from the LLM before parsing."""
        # Handle potential AIMessage objects or plain strings
        raw_content = ""
        if hasattr(input_data, 'content'):
            raw_content = input_data.content
            logger.info(f"Raw LLM output (AIMessage content) before parsing: {raw_content}")
        elif isinstance(input_data, str):
            raw_content = input_data
            logger.info(f"Raw LLM output (string) before parsing: {raw_content}")
        else:
            logger.warning(f"Unexpected LLM output type before parsing: {type(input_data)}. Data: {input_data}")
            raw_content = str(input_data) # Attempt to log string representation

        # Add specific checks for empty or invalid content
        if not raw_content.strip():
            logger.error("LLM output content is empty or whitespace only. Raising ValueError.")
            raise ValueError("LLM output is empty or contains only whitespace.")
        elif not raw_content.strip().startswith(("{", "[")): # Basic check for JSON start
             logger.error(f"LLM output content does not appear to start with valid JSON: {raw_content[:100]}... Raising ValueError.")
             raise ValueError(f"LLM output does not appear to be valid JSON. Starts with: {raw_content[:100]}")

        return input_data # Return the original data for the next step in the chain

    log_step = RunnableLambda(log_llm_output)

    log_prompt_step = RunnableLambda(log_formatted_prompt)
    log_output_step = RunnableLambda(log_llm_output)

    # Return the chained operations, now including logging for prompt and output
    return (
        prompt
        | log_prompt_step # Log the formatted prompt
        | bound_llm
        | log_output_step # Log the raw LLM output
        | parser # Use PydanticOutputParser for robust JSON parsing
    )

from core.state import NoteState
from langchain.output_parsers import PydanticOutputParser

def create_note_agent(
    llm: ChatOpenAI,
    tools: list,
    system_prompt: str,
) -> AgentExecutor:
    """
    Create a Note Agent that updates the entire state.
    """
    logger.info("Creating note agent")
    parser = PydanticOutputParser(pydantic_object=NoteState)
    output_format = parser.get_format_instructions()
    escaped_output_format = output_format.replace("{", "{{").replace("}", "}}")
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt+"\n\nPlease format your response as a JSON object with the following structure:\n"+escaped_output_format),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    logger.debug(f"Note agent prompt: {prompt}")
    agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)
    logger.info("Note agent created successfully")
    return AgentExecutor.from_agent_and_tools(
        agent=agent, 
        tools=tools, 
        verbose=False,
    )

logger.info("Agent creation module initialized")