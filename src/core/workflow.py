from typing import Dict, Any
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver

from .state import State
from .node import agent_node, human_choice_node, note_agent_node, human_review_node, refiner_node
from .router import QualityReview_router, hypothesis_router, process_router

from ..agents.hypothesis_agent import create_hypothesis_agent
from ..agents.process_agent import create_process_agent
from ..agents.visualization_agent import create_visualization_agent
from ..agents.code_agent import create_code_agent
from ..agents.search_agent import create_search_agent
from ..agents.report_agent import create_report_agent
from ..agents.quality_review_agent import create_quality_review_agent
from ..agents.note_agent import create_note_agent
from ..agents.refiner_agent import create_refiner_agent

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
        self.members = ["Hypothesis", "Process", "Visualization", "Search", "Coder", "Report", "QualityReview", "Refiner"]
        self.agents = self.create_agents()
        self.setup_workflow()

    def create_agents(self):
        """Create all system agents"""
        # Create agents dictionary
        agents = {}

        # Create each agent using their respective creation functions
        agents["hypothesis_agent"] = create_hypothesis_agent(
            self._create_model("hypothesis_agent"),
            self.members,
            self.working_directory
        )

        agents["process_agent"] = create_process_agent(self._create_model("process_agent"))

        agents["visualization_agent"] = create_visualization_agent(
            self._create_model("visualization_agent"),
            self.members,
            self.working_directory
        )

        agents["code_agent"] = create_code_agent(
            self._create_model("code_agent"),
            self.members,
            self.working_directory
        )

        agents["searcher_agent"] = create_search_agent(
            self._create_model("searcher_agent"),
            self.members,
            self.working_directory
        )

        agents["report_agent"] = create_report_agent(
            self._create_model("report_agent"),
            self.members,
            self.working_directory
        )

        agents["quality_review_agent"] = create_quality_review_agent(
            self._create_model("quality_review_agent"),
            self.members,
            self.working_directory
        )

        agents["note_agent"] = create_note_agent(self._create_model("note_agent"))

        agents["refiner_agent"] = create_refiner_agent(
            self._create_model("refiner_agent"),
            self.members,
            self.working_directory
        )

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
