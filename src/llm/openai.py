from typing import Type

from langchain_openai import ChatOpenAI

from .base import BaseProvider


class OpenAIProvider(BaseProvider):
    """Provider for OpenAI models."""

    def get_model_class(self) -> Type:
        """Returns the ChatOpenAI class."""
        return ChatOpenAI