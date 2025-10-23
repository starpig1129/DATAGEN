from ..logger import setup_logger
from ..llm.factory import ProviderFactory

class LanguageModelManager:
    def __init__(self):
        """Initialize the language model manager"""
        self.logger = setup_logger()
        self.provider_factory = ProviderFactory()
        self.provider_mapping = {
            "hypothesis_agent": "openai",
            "process_agent": "openai",
            "visualization_agent": "openai",
            "code_agent": "openai",
            "searcher_agent": "openai",
            "report_agent": "openai",
            "quality_review_agent": "openai",
            "note_agent": "openai",
            "refiner_agent": "openai"
        }
        self.model_configs = {
            "hypothesis_agent": {"model": "gpt-5-nano-2025-08-07", "temperature": 1.0},
            "process_agent": {"model": "gpt-5-mini-2025-08-07", "temperature": 1.0},
            "visualization_agent": {"model": "gpt-5-nano-2025-08-07", "temperature": 1.0},
            "code_agent": {"model": "gpt-5-mini-2025-08-07", "temperature": 1.0},
            "searcher_agent": {"model": "gpt-5-nano-2025-08-07", "temperature": 1.0},
            "report_agent": {"model": "gpt-5-mini-2025-08-07", "temperature": 1.0},
            "quality_review_agent": {"model": "gpt-5-nano-2025-08-07", "temperature": 1.0},
            "note_agent": {"model": "gpt-5-mini-2025-08-07", "model_kwargs": {"response_format": {"type": "json_object"}}, "temperature": 1.0},
            "refiner_agent": {"model": "gpt-5-mini-2025-08-07", "temperature": 1.0}
        }

    def get_provider(self, agent_name: str):
        """Get the provider for the given agent."""
        provider_name = self.provider_mapping.get(agent_name)
        if not provider_name:
            raise ValueError(f"No provider configured for agent '{agent_name}'")
        return self.provider_factory.create_provider(provider_name)

    def get_model_config(self, agent_name: str) -> dict:
        """Get the model configuration for the given agent."""
        config = self.model_configs.get(agent_name)
        if not config:
            raise ValueError(f"No model config configured for agent '{agent_name}'")
        return config
