from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """An abstract base class for all agents."""

    @abstractmethod
    def invoke(self, state: dict) -> dict:
        """
        Invokes the agent with a given state.

        Args:
            state: The current state of the workflow.

        Returns:
            A dictionary representing the updated state.
        """
        pass