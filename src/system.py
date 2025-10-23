import os
from typing import Dict, Any
from . import logger, load_cfg
from langchain_core.messages import HumanMessage

from .core import WorkflowManager, LanguageModelManager

class MultiAgentSystem:
    def __init__(self):
        self.logger = logger.setup_logger()
        self.setup_environment()
        self.lm_manager = LanguageModelManager()
        self.workflow_manager = WorkflowManager(
            language_models=self.lm_manager.get_models(),
            working_directory=load_cfg.WORKING_DIRECTORY
        )

    def setup_environment(self):
        """Initialize environment variables"""
        os.environ["OPENAI_API_KEY"] = load_cfg.OPENAI_API_KEY
        os.environ["LANGCHAIN_API_KEY"] = load_cfg.LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = "Multi-Agent Data Analysis System"

        if not os.path.exists(load_cfg.WORKING_DIRECTORY):
            os.makedirs(load_cfg.WORKING_DIRECTORY)
            self.logger.info(f"Created working directory: {load_cfg.WORKING_DIRECTORY}")

    def run(self, user_input: str) -> None:
        """Run the multi-agent system with user input"""
        graph = self.workflow_manager.get_graph()
        events = graph.stream(
            {
                "messages": [HumanMessage(content=user_input)],
                "hypothesis": "",
                "process_decision": "",
                "process": "",
                "visualization_state": "",
                "searcher_state": "",
                "code_state": "",
                "report_section": "",
                "quality_review": "",
                "needs_revision": False,
                "last_sender": "",
            },
            {"configurable": {"thread_id": "1"}, "recursion_limit": 3000},
            stream_mode="values",
            debug=False
        )
        
        for event in events:
            message = event["messages"][-1]
            if isinstance(message, tuple):
                print(message, end='', flush=True)
            else:
                message.pretty_print()