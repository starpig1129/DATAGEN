from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.output_parsers import PydanticOutputParser
from ..core.state import NoteState
from ..tools.FileEdit import read_document
from .base import BaseAgent


class NoteAgent(BaseAgent):
    """Agent responsible for taking notes on the research process."""

    def __init__(self, language_model_manager, team_members, working_directory='./data_storage/'):
        """
        Initialize the NoteAgent.

        Args:
            language_model_manager: Manager for language model configuration.
            team_members: List of team member roles for collaboration.
            working_directory: The directory where the agent's data will be stored.
        """
        # Set attributes as in BaseAgent
        self.agent_name = "note_agent"
        self.language_model_manager = language_model_manager
        self.team_members = team_members
        self.working_directory = working_directory

        # Create the language model
        self.llm = self._create_model()

        # Define tools and system prompt
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

        # Create the agent executor directly (moved from create_note_agent)
        parser = PydanticOutputParser(pydantic_object=NoteState)
        output_format = parser.get_format_instructions()
        escaped_output_format = output_format.replace("{", "{{").replace("}", "}}")
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt+"\n\nPlease format your response as a JSON object with the following structure:\n"+escaped_output_format),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        agent = create_openai_functions_agent(llm=self.llm, tools=tools, prompt=prompt)
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            verbose=False,
        )

    def _get_system_prompt(self) -> str:
        """Not used in this agent."""
        return ""

    def _get_tools(self):
        """Not used in this agent."""
        return []
