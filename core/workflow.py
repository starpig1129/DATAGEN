from typing import Dict, Any
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
# Import LanguageModelManager for type hinting
from .language_models import LanguageModelManager 
from core.state import State
from core.node import agent_node, human_choice_node, note_agent_node, human_review_node, refiner_node
from core.router import QualityReview_router, hypothesis_router, process_router
from agent.hypothesis_agent import create_hypothesis_agent
from agent.process_agent import create_process_agent
from agent.visualization_agent import create_visualization_agent
from agent.code_agent import create_code_agent
from agent.search_agent import create_search_agent
from agent.report_agent import create_report_agent
from agent.quality_review_agent import create_quality_review_agent
from agent.note_agent import create_note_agent
from agent.refiner_agent import create_refiner_agent

class WorkflowManager:
    def __init__(self, model_manager, working_directory):
        """
        Initialize the workflow manager with a language model manager and working directory.

        Args:
            model_manager (LanguageModelManager): Instance of the language model manager.
            working_directory (str): Path to the working directory.
        """
        self.model_manager = model_manager # Changed from language_models
        self.working_directory = working_directory
        self.workflow = None
        self.memory = None
        self.graph = None
        # Ensure agent names here match keys in config.yaml if used for model selection
        self.members = ["Hypothesis", "Process", "Visualization", "Search", "Coder", "Report", "QualityReview", "Refiner"]
        self.agents = self.create_agents()
        self.setup_workflow()

    def create_agents(self):
        """Create all system agents using models from LanguageModelManager"""
        # Create agents dictionary
        agents = {}

        # Create each agent using their respective creation functions and models from the manager
        agents["hypothesis_agent"] = create_hypothesis_agent(
            language_model_manager=self.model_manager, # Use manager
            agent_name="hypothesis_agent",
            members=self.members,
            working_directory=self.working_directory
        )

        agents["process_agent"] = create_process_agent(
            self.model_manager,
            agent_name="process_agent"
        )

        agents["visualization_agent"] = create_visualization_agent(
            language_model_manager=self.model_manager,
            agent_name="visualization_agent",
            members=self.members,
            working_directory=self.working_directory
        )

        agents["code_agent"] = create_code_agent(
            language_model_manager=self.model_manager,
            agent_name="code_agent",
            members=self.members,
            working_directory=self.working_directory
        )

        # Renamed key from "searcher_agent" to "search_agent" for consistency
        agents["search_agent"] = create_search_agent(
            language_model_manager=self.model_manager,
            agent_name="search_agent",
            members=self.members,
            working_directory=self.working_directory
        )

        agents["report_agent"] = create_report_agent(
            language_model_manager=self.model_manager,
            agent_name="report_agent",
            members=self.members,
            working_directory=self.working_directory
        )

        agents["quality_review_agent"] = create_quality_review_agent(
            language_model_manager=self.model_manager,
            agent_name="quality_review_agent",
            members=self.members,
            working_directory=self.working_directory
        )

        agents["note_agent"] = create_note_agent(
            self.model_manager,
            agent_name="note_agent",
        )

        agents["refiner_agent"] = create_refiner_agent(
            language_model_manager=self.model_manager,
            agent_name="refiner_agent",
            members=self.members,
            working_directory=self.working_directory
        )

        return agents

    def setup_workflow(self):
        """Set up the workflow graph"""
        self.workflow = StateGraph(State)

        # Add nodes - Ensure agent names match the keys in self.agents dictionary
        self.workflow.add_node("Hypothesis", lambda state: agent_node(state, self.agents["hypothesis_agent"], "hypothesis_agent"))
        self.workflow.add_node("Process", lambda state: agent_node(state, self.agents["process_agent"], "process_agent"))
        self.workflow.add_node("Visualization", lambda state: agent_node(state, self.agents["visualization_agent"], "visualization_agent"))
        # Updated node name to match agent key
        self.workflow.add_node("Search", lambda state: agent_node(state, self.agents["search_agent"], "search_agent"))
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

        # Compile workflow with checkpointer (追蹤功能已禁用)
        self.memory = MemorySaver()
        
        # 添加診斷日誌
        import logging
        logger = logging.getLogger(__name__)
        logger.info("正在初始化 MemorySaver 用於工作流程 (LangChain 追蹤已禁用)")
        logger.info(f"MemorySaver 類型: {type(self.memory)}")
        
        # 編譯工作流程 - 追蹤功能已在環境變數中禁用
        self.graph = self.workflow.compile(checkpointer=self.memory)
        
        logger.info("工作流程編譯成功，LangChain 追蹤已禁用")

    def get_graph(self):
        """Return the compiled workflow graph"""
        return self.graph
