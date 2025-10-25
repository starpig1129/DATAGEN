import sys
from pathlib import Path

# 調整路徑以支援模組導入
backend_path = str(Path(__file__).resolve().parent.parent.parent)
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from src.logger import setup_logger
from src.llm.factory import ProviderFactory
from config.settings import AGENT_MODELS

class LanguageModelManager:
    def __init__(self):
        """Initialize the language model manager"""
        self.logger = setup_logger() if callable(setup_logger) else None
        self.provider_factory = ProviderFactory()

    def get_provider(self, agent_name: str):
        """Get the provider for the given agent."""
        provider_name = AGENT_MODELS.get_provider(agent_name)
        if not provider_name:
            raise ValueError(f"No provider configured for agent '{agent_name}'")
        return self.provider_factory.create_provider(provider_name)

    def get_model_config(self, agent_name: str) -> dict:
        """Get the model configuration for the given agent."""
        config = AGENT_MODELS.get_model_config(agent_name)
        if not config:
            raise ValueError(f"No model config configured for agent '{agent_name}'")
        return config
