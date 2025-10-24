from typing import Type

from langchain_openai import AzureChatOpenAI

from .base import BaseProvider


class AzureChatOpenAIProvider(BaseProvider):
    """Provider for Azure OpenAI models."""

    def get_model_class(self) -> Type:
        """Returns the AzureChatOpenAI class."""
        return AzureChatOpenAI