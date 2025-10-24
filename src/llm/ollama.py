from typing import Type
from langchain_ollama import ChatOllama

from .base import BaseProvider

class OllamaProvider(BaseProvider):
    """Provider for Ollama models."""

    def get_model_class(self) -> Type:
        """Returns the ChatOllama class."""
        return ChatOllama