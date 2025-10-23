from .openai import OpenAIProvider


class ProviderFactory:
    """A factory class for creating LLM providers."""

    def create_provider(self, provider_name: str, **kwargs):
        """
        Creates a provider instance based on the provider name.

        Args:
            provider_name: The name of the provider to create.
            **kwargs: Additional keyword arguments for provider configuration.

        Returns:
            An instance of the requested provider.

        Raises:
            NotImplementedError: If the provider creation is not implemented.
        """
        if provider_name == "openai":
            return OpenAIProvider()
        else:
            raise NotImplementedError(f"Provider creation for '{provider_name}' is not implemented.")