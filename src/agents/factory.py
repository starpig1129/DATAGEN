class AgentFactory:
    """A factory class for creating agents."""

    def create_agent(self, agent_name: str, **kwargs):
        """
        Creates an agent instance based on the agent name.

        Args:
            agent_name: The name of the agent to create.
            **kwargs: Additional keyword arguments for agent configuration.

        Returns:
            An instance of the requested agent.

        Raises:
            NotImplementedError: If the agent creation is not implemented.
        """
        raise NotImplementedError(f"Agent creation for '{agent_name}' is not implemented.")