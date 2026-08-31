from __future__ import annotations

import os
from typing import Any, Type

from langchain_openai import ChatOpenAI

from .base import BaseProvider

# OrcaRouter is an OpenAI-compatible AI gateway. Model IDs follow the
# "orcarouter/<model>" namespace (e.g. orcarouter/fusion-mini).
ORCAROUTER_BASE_URL = "https://api.orcarouter.ai/v1"


class OrcaRouterChatOpenAI(ChatOpenAI):
    """ChatOpenAI preconfigured for the OrcaRouter gateway."""

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("base_url", ORCAROUTER_BASE_URL)
        kwargs.setdefault("api_key", os.getenv("ORCAROUTER_API_KEY"))
        super().__init__(**kwargs)


class OrcaRouterProvider(BaseProvider):
    """Provider for OrcaRouter models."""

    def get_model_class(self) -> Type:
        """Returns the OrcaRouterChatOpenAI class."""
        return OrcaRouterChatOpenAI
