from langchain.agents import create_openai_functions_agent, AgentExecutor, create_tool_calling_agent  # Added create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda  # Added RunnableLambda
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI  # Added Google
from langchain_community.chat_models import ChatOllama  # Added Ollama
from typing import List, Union, Literal
from pydantic import BaseModel, Field
from langchain.tools import tool
import os
import time
import json
import uuid

from logger import setup_logger

# New core modules for capability detection, prompt templates, and robust parsing
from core.tool_binding import detect_capabilities, build_tool_schema, bind_or_route, RouteSchema as RouterDecision, route_then_execute
from core.prompt_templates import json_only_base_prompt, router_stage1_decision_prompt
from core.output_guard import guarded_parse

# Set up logger
logger = setup_logger()

# 診斷計數器
api_call_counter = 0
empty_response_counter = 0
retry_counter = 0

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
    llm: Union[ChatOpenAI, ChatAnthropic, ChatGoogleGenerativeAI, ChatOllama],  # Expanded type hint
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

    # Capability detection and unified tool binding/routing
    caps = detect_capabilities(llm)
    logger.info(f"Detected LLM capabilities: family={caps.family}, native_tools={caps.native_tools}, force_tool={caps.force_tool}, json_mode={caps.json_mode}")

    # Standardize tool schema for binding or routing
    try:
        # LangChain tools decorated by @tool expose args schema via .args or .args_schema; we best-effort wrap
        tool_schemas = []
        for t in tools:
            args_schema = getattr(t, "args_schema", None)
            if args_schema is None:
                # Fallback: create a minimal empty-args schema
                class _Empty(BaseModel):
                    pass
                schema_model = _Empty
            else:
                schema_model = args_schema
            tool_schemas.append(build_tool_schema(schema_model, name=getattr(t, "name", t.name), description=getattr(t, "description", "")))
    except Exception as e:
        logger.error(f"Failed to build tool schemas: {e}")
        tool_schemas = []

    bound_or_llm, bind_meta = bind_or_route(llm, tool_schemas, capabilities=None, force=True)
    logger.info(f"Tool binding mode: {bind_meta.get('mode')} (family={bind_meta.get('family')})")

    # If we have native forced tool binding (OpenAI), use LangChain's create_tool_calling_agent directly
    if bind_meta.get("mode") == "bind":
        logger.info(f"Using create_tool_calling_agent with native tool binding for model type: {type(llm)}")
        agent = create_tool_calling_agent(bound_or_llm, tools, prompt)
        logger.info("Agent runnable created successfully with native binding")
        return AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=False)

    # Otherwise, implement two-stage routing:
    # Stage 1: Ask model to choose next action via JSON-only router prompt
    from langchain_core.prompts import ChatPromptTemplate as _CPT
    route_prompt = _CPT.from_messages([
        ("system", json_only_base_prompt(
            task_instruction="Decide the next action strictly as JSON.",
            schema_json=RouterDecision.model_json_schema(),
            extra_notes="Choose a tool by name if beneficial, else FINISH. Provide arguments under 'input'."
        )),
        ("system", router_stage1_decision_prompt([ts.model_dump() for ts in tool_schemas])),
        MessagesPlaceholder(variable_name="messages"),
    ])

    def _router_invoke(messages):
        # Run the router model to produce a JSON decision
        trace_id = str(uuid.uuid4())
        logger.info(f"[router] invoking stage-1 decision, trace_id={trace_id}")
        raw = llm.invoke(route_prompt.format_prompt(messages=messages))
        raw_text = getattr(raw, "content", raw)
        parsed = guarded_parse(str(raw_text), schema=RouterDecision, allow_repair=True, trace_id=trace_id)
        if not parsed["ok"]:
            # L2 parse retry: strictly instruct JSON-only and retry once
            logger.warning(f"[router] parse failed, retrying once. err={parsed['error']}, trace_id={trace_id}")
            retry_prompt = _CPT.from_messages([
                ("system", json_only_base_prompt(
                    task_instruction="Your previous output was not valid JSON. Output ONLY valid JSON following the schema.",
                    schema_json=RouterDecision.model_json_schema(),
                    extra_notes="No text outside JSON. First character must be {."
                )),
                MessagesPlaceholder(variable_name="messages"),
            ])
            raw2 = llm.invoke(retry_prompt.format_prompt(messages=messages))
            raw_text2 = getattr(raw2, "content", raw2)
            parsed = guarded_parse(str(raw_text2), schema=RouterDecision, allow_repair=True, trace_id=trace_id)

        if not parsed["ok"]:
            # Final fallback to FINISH minimal response
            logger.error(f"[router] parse ultimately failed. Falling back to FINISH. trace_id={trace_id}")
            return RouterDecision(next="FINISH", input={}, explanation="fallback due to parse failure")
        return parsed["data"]

    # Stage 2: Execute chosen tool explicitly and feed back results if needed.
    def _execute_and_reply(messages):
        decision = _router_invoke(messages)
        name_to_callable = {getattr(t, "name", t.name): t for t in tools}
        status, tool_res = route_then_execute(decision, name_to_callable)
        # Produce final AI message as JSON for the agent loop
        from langchain.schema import AIMessage
        final_payload = {
            "next": decision.next,
            "input": decision.input,
            "tool_status": status,
            "tool_result": tool_res,
        }
        return AIMessage(content=json.dumps(final_payload, ensure_ascii=False))

    # Compose runnable chain: prompt -> llm (only used in router) -> explicit tool execution
    router_chain = RunnableLambda(lambda x: x) | RunnableLambda(_execute_and_reply)

    logger.info("Agent runnable created successfully via two-stage routing")
    
    # Return an executor to manage the agent's task execution
    return AgentExecutor.from_agent_and_tools(agent=router_chain, tools=tools, verbose=False)


def create_supervisor(
    llm: Union[ChatOpenAI, ChatAnthropic, ChatGoogleGenerativeAI, ChatOllama], # Expanded type hint
    system_prompt: str,
    members: list[str]
) -> AgentExecutor:
    """Create a supervisor agent with unified capability detection and robust JSON handling."""
    logger.info("Creating supervisor")
    
    # Define options for routing, including FINISH and team members
    options = ["FINISH"] + members

    # Define Pydantic schema for routing decisions
    class RouteSchema(BaseModel):
        """Schema for routing decisions."""
        next: str = Field(description=f"The next agent to route to or 'FINISH'. Must be one of {options}")
        task: str = Field(description="The task description for the next agent")

    # Create a simplified prompt template
    system_message_content = f"""You are a research supervisor.

Select the next agent from: {str(options)}

Respond only with JSON format having 'next' and 'task' fields.

Use "FINISH" when complete."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message_content),
        MessagesPlaceholder(variable_name="messages"),
        ("system", "Respond with JSON only:")
    ])

    # Capability detection and unified tool binding/routing
    caps = detect_capabilities(llm)
    logger.info(f"Detected LLM capabilities: family={caps.family}, native_tools={caps.native_tools}, force_tool={caps.force_tool}, json_mode={caps.json_mode}")

    # Standardize tool schema for binding or routing
    tool_schemas = [build_tool_schema(RouteSchema, name="route", description="Select the next role and assign a task based on the conversation.")]

    bound_or_llm, bind_meta = bind_or_route(llm, tool_schemas, capabilities=caps, force=True)
    logger.info(f"Tool binding mode: {bind_meta.get('mode')} (family={bind_meta.get('family')})")

    # If we have native forced tool binding (OpenAI), use LangChain's create_tool_calling_agent directly
    if bind_meta.get("mode") == "bind":
        logger.info(f"Using create_tool_calling_agent with native tool binding for model type: {type(llm)}")
        agent = create_tool_calling_agent(bound_or_llm, [lambda x: x], prompt)  # Dummy tool for compatibility
        logger.info("Supervisor agent runnable created successfully with native binding")
        return AgentExecutor.from_agent_and_tools(agent=agent, tools=[lambda x: x], verbose=False)

    # Otherwise, implement two-stage routing:
    # Stage 1: Ask model to choose next action via JSON-only router prompt
    from langchain_core.prompts import ChatPromptTemplate as _CPT
    route_prompt = _CPT.from_messages([
        ("system", json_only_base_prompt(
            task_instruction="Decide the next action strictly as JSON.",
            schema_json=RouteSchema.model_json_schema(),
            extra_notes="Choose a team member or FINISH. Provide task description under 'task'."
        )),
        MessagesPlaceholder(variable_name="messages"),
    ])

    def _router_invoke(messages):
        # Run the router model to produce a JSON decision
        trace_id = str(uuid.uuid4())
        logger.info(f"[supervisor.router] invoking decision, trace_id={trace_id}")
        raw = llm.invoke(route_prompt.format_prompt(messages=messages))
        raw_text = getattr(raw, "content", raw)
        parsed = guarded_parse(str(raw_text), schema=RouteSchema, allow_repair=True, trace_id=trace_id)
        if not parsed["ok"]:
            # L2 parse retry: strictly instruct JSON-only and retry once
            logger.warning(f"[supervisor.router] parse failed, retrying once. err={parsed['error']}, trace_id={trace_id}")
            retry_prompt = _CPT.from_messages([
                ("system", json_only_base_prompt(
                    task_instruction="Your previous output was not valid JSON. Output ONLY valid JSON following the schema.",
                    schema_json=RouteSchema.model_json_schema(),
                    extra_notes="No text outside JSON. First character must be {."
                )),
                MessagesPlaceholder(variable_name="messages"),
            ])
            raw2 = llm.invoke(retry_prompt.format_prompt(messages=messages))
            raw_text2 = getattr(raw2, "content", raw2)
            parsed = guarded_parse(str(raw_text2), schema=RouteSchema, allow_repair=True, trace_id=trace_id)

        if not parsed["ok"]:
            # Final fallback to FINISH minimal response
            logger.error(f"[supervisor.router] parse ultimately failed. Falling back to FINISH. trace_id={trace_id}")
            return RouteSchema(next="FINISH", task="fallback due to parse failure")
        return parsed["data"]

    # Stage 2: Return the decision as an AIMessage
    def _execute_and_reply(messages):
        decision = _router_invoke(messages)
        from langchain.schema import AIMessage
        return AIMessage(content=decision.json())

    # Compose runnable chain: prompt -> llm (only used in router) -> explicit tool execution
    router_chain = RunnableLambda(lambda x: x) | RunnableLambda(_execute_and_reply)

    logger.info("Supervisor agent runnable created successfully via two-stage routing")
    
    # Return an executor to manage the agent's task execution
    return AgentExecutor.from_agent_and_tools(agent=router_chain, tools=[lambda x: x], verbose=False)

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