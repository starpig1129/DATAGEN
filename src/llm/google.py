from typing import Type
from langchain_google_genai import ChatGoogleGenerativeAI
from .base import BaseProvider

class GoogleProvider(BaseProvider):
    """Provider for Google models."""

    def get_model_class(self) -> Type:
        """Returns the ChatGoogleGenerativeAI class."""
        return ChatGoogleGenerativeAI