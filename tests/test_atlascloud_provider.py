"""Tests for the optional Atlas Cloud LLM provider."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.llm.atlascloud import AtlasCloudChatOpenAI, AtlasCloudProvider
from src.llm.factory import ProviderFactory


def test_factory_creates_atlascloud_provider() -> None:
    provider = ProviderFactory().create_provider("atlascloud")

    assert isinstance(provider, AtlasCloudProvider)
    assert provider.get_model_class() is AtlasCloudChatOpenAI


def test_atlascloud_model_uses_compatible_endpoint_without_retries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ATLASCLOUD_API_KEY", "test-key")

    with patch("src.llm.atlascloud.ChatOpenAI.__init__", return_value=None) as init:
        AtlasCloudChatOpenAI(model="openai/gpt-5.4", temperature=1.0)

    init.assert_called_once_with(
        api_key="test-key",
        model="openai/gpt-5.4",
        temperature=1.0,
        base_url="https://api.atlascloud.ai/v1",
        max_retries=0,
    )


def test_atlascloud_model_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ATLASCLOUD_API_KEY", raising=False)

    with pytest.raises(ValueError, match="ATLASCLOUD_API_KEY"):
        AtlasCloudChatOpenAI(model="openai/gpt-5.4")
