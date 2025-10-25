from typing import Type
from langchain_anthropic import ChatAnthropic
from .base import BaseProvider

class AnthropicProvider(BaseProvider):
    """Provider for Anthropic models."""

    def get_model_class(self) -> Type:
        """Returns the ChatAnthropic class."""
        return ChatAnthropic