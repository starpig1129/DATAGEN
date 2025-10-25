from typing import Type

from langchain_groq import ChatGroq

from .base import BaseProvider


class ChatGrokProvider(BaseProvider):
    """Provider for ChatGrok models."""

    def get_model_class(self) -> Type:
        """Returns the ChatGroq class."""
        return ChatGroq