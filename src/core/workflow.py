from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver

from .state import State
from .node import agent_node, human_choice_node, note_agent_node, human_review_node, refiner_node
from .router import QualityReview_router, hypothesis_router, process_router

from ..agents.factory import AgentFactory


class WorkflowManager:
    def __init__(self, lm_manager, working_directory):
        """
        Initialize the workflow manager with language model manager and working directory.
        
        Args:
            lm_manager: The LanguageModelManager instance
            working_directory (str): Path to the working directory
        """
        self.lm_manager = lm_manager
        self.working_directory = working_directory
        self.workflow = None
        self.memory = None
        self.graph = None
        self.members = ["Hypothesis", "Process", "Visualization", "Search", "Coder", "Report", "QualityReview", "note", "Refiner"]
        self.agents = self.create_agents()
        self.setup_workflow()

    def create_agents(self):
        """Create all system agents"""
        # Create agents dictionary
        agents = {}

        # Create agent factory
        agent_factory = AgentFactory(
            language_model_manager=self.lm_manager,
            team_members=self.members,
            working_directory=self.working_directory
        )

        # Create each agent using the factory
        agents["hypothesis_agent"] = agent_factory.create_agent("hypothesis_agent")

        agents["process_agent"] = agent_factory.create_agent("process_agent")

        agents["visualization_agent"] = agent_factory.create_agent("visualization_agent")

        agents["code_agent"] = agent_factory.create_agent("code_agent")

        agents["searcher_agent"] = agent_factory.create_agent("searcher_agent")

        agents["report_agent"] = agent_factory.create_agent("report_agent")

        agents["quality_review_agent"] = agent_factory.create_agent("quality_review_agent")

        agents["note_agent"] = agent_factory.create_agent("note_agent")

        agents["refiner_agent"] = agent_factory.create_agent("refiner_agent")

        return agents

    def _create_model(self, agent_name: str):
        """Create a model instance for the given agent."""
        provider = self.lm_manager.get_provider(agent_name)
        model_class = provider.get_model_class()
        config = self.lm_manager.get_model_config(agent_name)
        return model_class(**config)

    def setup_workflow(self):
        """Set up the workflow graph"""
        self.workflow = StateGraph(State)
        
        # Add nodes
        self.workflow.add_node("Hypothesis", lambda state: agent_node(state, self.agents["hypothesis_agent"], "hypothesis_agent"))
        self.workflow.add_node("Process", lambda state: agent_node(state, self.agents["process_agent"], "process_agent"))
        self.workflow.add_node("Visualization", lambda state: agent_node(state, self.agents["visualization_agent"], "visualization_agent"))
        self.workflow.add_node("Search", lambda state: agent_node(state, self.agents["searcher_agent"], "searcher_agent"))
        self.workflow.add_node("Coder", lambda state: agent_node(state, self.agents["code_agent"], "code_agent"))
        self.workflow.add_node("Report", lambda state: agent_node(state, self.agents["report_agent"], "report_agent"))
        self.workflow.add_node("QualityReview", lambda state: agent_node(state, self.agents["quality_review_agent"], "quality_review_agent"))
        self.workflow.add_node("NoteTaker", lambda state: note_agent_node(state, self.agents["note_agent"], "note_agent"))
        self.workflow.add_node("HumanChoice", human_choice_node)
        self.workflow.add_node("HumanReview", human_review_node)
        self.workflow.add_node("Refiner", lambda state: refiner_node(state, self.agents["refiner_agent"], "refiner_agent"))

        # Add edges
        self.workflow.add_edge(START, "Hypothesis")
        self.workflow.add_edge("Hypothesis", "HumanChoice")
        
        self.workflow.add_conditional_edges(
            "HumanChoice",
            hypothesis_router,
            {
                "Hypothesis": "Hypothesis",
                "Process": "Process"
            }
        )

        self.workflow.add_conditional_edges(
            "Process",
            process_router,
            {
                "Coder": "Coder",
                "Search": "Search",
                "Visualization": "Visualization",
                "Report": "Report",
                "Process": "Process",
                "Refiner": "Refiner",
            }
        )

        for member in ["Visualization", 'Search', 'Coder', 'Report']:
            self.workflow.add_edge(member, "QualityReview")

        self.workflow.add_conditional_edges(
            "QualityReview",
            QualityReview_router,
            {
                'Visualization': "Visualization",
                'Search': "Search",
                'Coder': "Coder",
                'Report': "Report",
                'NoteTaker': "NoteTaker",
            }
        )

        self.workflow.add_edge("NoteTaker", "Process")
        self.workflow.add_edge("Refiner", "HumanReview")
        
        self.workflow.add_conditional_edges(
            "HumanReview",
            lambda state: "Process" if state and state.get("needs_revision", False) else "END",
            {
                "Process": "Process",
                "END": END
            }
        )

        # Compile workflow
        self.memory = MemorySaver()
        self.graph = self.workflow.compile()

    def get_graph(self):
        """Return the compiled workflow graph"""
        return self.graph
