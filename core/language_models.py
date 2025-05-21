import os
import json
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama
from logger import setup_logger

class LanguageModelManager:
    def __init__(self):
        """Initialize the language model manager"""
        self.logger = setup_logger()
        self.agent_configs = {}
        self.openai_models = {}
        self.claude_models = {}
        self.gemini_models = {}
        self.ollama_models = {}
        
        self.load_agent_configs()
        self.initialize_llms()

    def load_agent_configs(self):
        """Load agent model configurations from JSON file."""
        config_path = os.getenv("AGENT_MODEL_CONFIG_PATH", "agent_model_config.json")
        try:
            with open(config_path, 'r') as f:
                self.agent_configs = json.load(f)
            self.logger.info(f"Agent model configurations loaded successfully from {config_path}.")
        except FileNotFoundError:
            self.logger.error(f"Agent model configuration file not found at {config_path}. No models will be configured.")
            self.agent_configs = {}
        except json.JSONDecodeError:
            self.logger.error(f"Error decoding JSON from agent model configuration file at {config_path}.")
            self.agent_configs = {}
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while loading agent model configurations from {config_path}: {str(e)}")
            self.agent_configs = {}

    def initialize_llms(self):
        """Initialize language models based on agent configurations."""
        if not self.agent_configs:
            self.logger.warning("No agent configurations loaded. Skipping LLM initialization.")
            return

        for agent_name, config in self.agent_configs.items():
            provider = config.get("provider")
            model_name = config.get("model_name")
            model_kwargs = config.get("model_kwargs", {}) # For OpenAI JSON mode etc.
            temperature = config.get("temperature", 0) # Default temperature
            max_tokens = config.get("max_tokens", 4096) # Default max_tokens

            if not provider or not model_name:
                self.logger.warning(f"Skipping agent '{agent_name}': 'provider' or 'model_name' missing in config.")
                continue

            model_key = f"{provider}_{model_name}"
            # Add model_kwargs to the key if they are present to differentiate models with same name but different kwargs
            if model_kwargs:
                model_key += f"_kwargs_{json.dumps(model_kwargs, sort_keys=True)}"


            try:
                if provider == "openai":
                    if model_key not in self.openai_models:
                        api_key = os.getenv("OPENAI_API_KEY")
                        if not api_key:
                            self.logger.warning(f"OPENAI_API_KEY not found. Skipping OpenAI model '{model_name}' for agent '{agent_name}'.")
                            continue
                        self.logger.debug(f"Attempting to initialize OpenAI model. Name: {model_name}, Type: {type(model_name)}")
                        self.logger.debug(f"Temperature: {temperature}, Type: {type(temperature)}")
                        self.logger.debug(f"Max Tokens: {max_tokens}, Type: {type(max_tokens)}")
                        self.logger.debug(f"API Key (first 5 chars): {api_key[:5] if api_key else 'None'}, Type: {type(api_key)}")
                        self.logger.debug(f"Model Kwargs: {model_kwargs}, Type: {type(model_kwargs)}")
                        
                        try:
                            self.openai_models[model_key] = ChatOpenAI(
                                model=model_name,
                                temperature=temperature,
                                max_tokens=max_tokens,
                                api_key=api_key,
                                model_kwargs=model_kwargs # Pass directly, {} is fine
                            )
                            self.logger.info(f"Initialized OpenAI model '{model_name}' (Key: {model_key}) for agent '{agent_name}'.")
                        except TypeError as te:
                            self.logger.error(f"TypeError during OpenAI model '{model_name}' init for agent '{agent_name}': {str(te)}. Args: model_name='{model_name}', temp={temperature}, max_tokens={max_tokens}, model_kwargs={model_kwargs}")
                            # Potentially re-raise or handle as per existing logic
                            raise # Re-raise to see if it's the same error as before
                        except Exception as e: # Catch any other exception
                            self.logger.error(f"Unexpected error during OpenAI model '{model_name}' init for agent '{agent_name}': {type(e).__name__} - {str(e)}")
                            raise # Re-raise
                
                elif provider == "anthropic":
                    if model_key not in self.claude_models:
                        api_key = os.getenv("ANTHROPIC_API_KEY")
                        if not api_key:
                            self.logger.warning(f"ANTHROPIC_API_KEY not found. Skipping Anthropic model '{model_name}' for agent '{agent_name}'.")
                            continue
                        # Anthropic uses max_tokens_to_sample
                        self.claude_models[model_key] = ChatAnthropic(
                            model=model_name,
                            api_key=api_key,
                            temperature=temperature,
                            max_tokens_to_sample=max_tokens # Renamed for Anthropic
                        )
                        self.logger.info(f"Initialized Anthropic model '{model_name}' (Key: {model_key}) for agent '{agent_name}'.")

                elif provider == "google":
                    if model_key not in self.gemini_models:
                        api_key = os.getenv("GOOGLE_API_KEY")
                        if not api_key:
                            self.logger.warning(f"GOOGLE_API_KEY not found. Skipping Google model '{model_name}' for agent '{agent_name}'.")
                            continue
                        # Google's ChatGoogleGenerativeAI uses max_output_tokens, often handled by wrapper
                        self.gemini_models[model_key] = ChatGoogleGenerativeAI(
                            model=model_name,
                            google_api_key=api_key,
                            temperature=temperature,
                            max_output_tokens=max_tokens if max_tokens else None 
                        )
                        self.logger.info(f"Initialized Google model '{model_name}' (Key: {model_key}) for agent '{agent_name}'. Configured with max_tokens: {max_tokens}")

                elif provider == "ollama":
                    if model_key not in self.ollama_models:
                        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
                        # Ollama specific env vars for model names if needed, or direct from config
                        ollama_specific_model_name = os.getenv(f"OLLAMA_MODEL_NAME_{agent_name.upper()}", model_name)
                        
                        self.ollama_models[model_key] = ChatOllama(
                            base_url=base_url,
                            model=ollama_specific_model_name,
                            temperature=temperature
                        )
                        self.logger.info(f"Initialized Ollama model '{ollama_specific_model_name}' (Key: {model_key}) for agent '{agent_name}' at {base_url}.")
                
                else:
                    self.logger.warning(f"Unsupported provider '{provider}' for agent '{agent_name}'.")

            except Exception as e:
                self.logger.error(f"Error initializing model '{model_name}' for provider '{provider}' (Agent: '{agent_name}'): {str(e)}")

    def get_model_for_agent(self, agent_name: str):
        """Return the initialized language model for a specific agent."""
        agent_config = self.agent_configs.get(agent_name)
        if not agent_config:
            self.logger.warning(f"No configuration found for agent '{agent_name}'. Cannot retrieve model.")
            return None

        provider = agent_config.get("provider")
        model_name = agent_config.get("model_name")
        model_kwargs = agent_config.get("model_kwargs", {})

        if not provider or not model_name:
            self.logger.warning(f"Provider or model_name missing in config for agent '{agent_name}'.")
            return None

        model_key = f"{provider}_{model_name}"
        if model_kwargs:
            model_key += f"_kwargs_{json.dumps(model_kwargs, sort_keys=True)}"

        model = None
        if provider == "openai":
            model = self.openai_models.get(model_key)
        elif provider == "anthropic":
            model = self.claude_models.get(model_key)
        elif provider == "google":
            model = self.gemini_models.get(model_key)
        elif provider == "ollama":
            model = self.ollama_models.get(model_key)
        
        if not model:
            self.logger.warning(f"Model with key '{model_key}' for agent '{agent_name}' not found or not initialized.")
            # Optionally, try to initialize it here if not found (on-demand initialization)
            # For now, we assume initialize_llms has already run.
        
        return model

    def get_models(self):
        """Return a flat dictionary of all initialized language models, keyed by their unique model identifier."""
        all_models = {}
        
        # The model_key is already unique (e.g., "openai_gpt-4o-mini_kwargs_{...}")
        # and is the key in these dictionaries.
        for model_key, model_instance in self.openai_models.items():
            all_models[model_key] = model_instance
            
        for model_key, model_instance in self.claude_models.items():
            all_models[model_key] = model_instance
            
        for model_key, model_instance in self.gemini_models.items():
            all_models[model_key] = model_instance
            
        for model_key, model_instance in self.ollama_models.items():
            all_models[model_key] = model_instance
            
        if not all_models:
            self.logger.info("No models have been initialized or are available in get_models().")
            
        return all_models
