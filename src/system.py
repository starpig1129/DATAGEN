import logging
# from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

from . import config
from .core.workflow import WorkflowManager
from .core.language_models import LanguageModelManager
from .core.state import create_initial_state

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MultiAgentSystem:
    def __init__(self):
        # Config is already loaded on import
        self.memory = MemorySaver()
        self.lm_manager = LanguageModelManager()
        self.workflow_manager = WorkflowManager(
            lm_manager=self.lm_manager,
            working_directory=config.WORKING_DIRECTORY
        )

    def run(self, user_input: str) -> None:
        graph = self.workflow_manager.get_graph()
        
        # Use factory function for consistent state initialization
        initial_state = create_initial_state(user_input)
        
        events = graph.stream(
            initial_state,
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

if __name__ == "__main__":
    system = MultiAgentSystem()
    user_input = input("Please enter your research topic: ")
    system.run(user_input)