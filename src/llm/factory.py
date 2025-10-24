from .openai import OpenAIProvider
from .anthropic import AnthropicProvider
from .google import GoogleProvider
from .ollama import OllamaProvider


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
        elif provider_name == "anthropic":
            return AnthropicProvider()
        elif provider_name == "google":
            return GoogleProvider()
        elif provider_name == "ollama":
            return OllamaProvider()
        else:
            raise NotImplementedError(f"Provider creation for '{provider_name}' is not implemented.")