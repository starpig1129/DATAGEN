# Import necessary libraries
import yaml
import os
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama
from logger import setup_logger
# import os # Needed to check for API keys - Already imported above

DEFAULT_CONFIG = {
    'default_model': {
        'provider': 'openai',
        'model_name': 'gpt-4o-mini'
    },
    'json_model': { # Specific model for JSON output
        'provider': 'openai',
        'model_name': 'gpt-4o'
    },
    'agents': {} # Placeholder for agent-specific models
}

def load_model_config(config_path='config.yaml'):
    """Loads model configuration from a YAML file."""
    logger = setup_logger()
    try:
        # Check if config file exists
        if not os.path.exists(config_path):
            logger.warning(f"Configuration file '{config_path}' not found. Using default model settings.")
            # Create a default config.yaml if it doesn't exist, based on the example
            example_path = 'config.yaml.example'
            if os.path.exists(example_path):
                try:
                    with open(example_path, 'r') as f_example, open(config_path, 'w') as f_config:
                        f_config.write(f_example.read())
                    logger.info(f"Created default '{config_path}' from example.")
                    # Try loading the newly created config file
                    with open(config_path, 'r') as f:
                        config = yaml.safe_load(f)
                        # Merge with defaults to ensure all keys exist
                        merged_config = DEFAULT_CONFIG.copy()
                        # Deep merge might be better, but for this structure, update should suffice
                        if config: # Check if config is not None
                            if 'default_model' in config:
                                merged_config['default_model'].update(config['default_model'])
                            if 'json_model' in config:
                                merged_config['json_model'].update(config['json_model'])
                            if 'agents' in config:
                                merged_config['agents'].update(config['agents'])
                        return merged_config
                except Exception as e:
                    logger.error(f"Error creating/reading default config file '{config_path}': {e}")
                    return DEFAULT_CONFIG # Fallback to hardcoded defaults
            else:
                logger.warning(f"Example config '{example_path}' not found. Cannot create default config.")
                return DEFAULT_CONFIG # Fallback to hardcoded defaults

        # Load existing config file
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            if not config:
                logger.warning(f"Configuration file '{config_path}' is empty. Using default model settings.")
                return DEFAULT_CONFIG
            # Merge with defaults to ensure all keys exist
            merged_config = DEFAULT_CONFIG.copy()
            # Deep merge might be better, but for this structure, update should suffice
            if 'default_model' in config:
                merged_config['default_model'].update(config['default_model'])
            if 'json_model' in config:
                 merged_config['json_model'].update(config['json_model'])
            if 'agents' in config:
                merged_config['agents'].update(config['agents'])
            logger.info(f"Loaded model configuration from '{config_path}'.")
            return merged_config
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file '{config_path}': {e}. Using default model settings.")
        return DEFAULT_CONFIG
    except Exception as e:
        logger.error(f"Error loading configuration file '{config_path}': {e}. Using default model settings.")
        return DEFAULT_CONFIG

class LanguageModelManager:
    def __init__(self, config_path='config.yaml'):
        """Initialize the language model manager"""
        self.logger = setup_logger()
        self.config = load_model_config(config_path)
        self.models = {} # Cache for initialized models { (provider, model_name, is_json): model_instance }

    def _initialize_model(self, provider, model_name, is_json_model=False):
        """Initializes a single language model instance based on provider and name."""
        cache_key = (provider, model_name, is_json_model)
        if cache_key in self.models:
            return self.models[cache_key]

        model_instance = None
        api_key_env_var = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'google': 'GOOGLE_API_KEY',
            'ollama': None # Ollama typically doesn't require an API key via env var
        }.get(provider)

        # Check for API key if required
        if api_key_env_var and not os.getenv(api_key_env_var):
            self.logger.warning(f"{api_key_env_var} not found. Cannot initialize {provider} model '{model_name}'.")
            return None

        # Common parameters (can be customized further if needed from config)
        params = {'model': model_name, 'temperature': 0, 'max_tokens': 4096}
        if provider == 'google':
             params['convert_system_message_to_human'] = True # Specific to Google model

        try:
            if provider == 'openai':
                if is_json_model:
                    # Ensure the specified model actually supports JSON mode if possible
                    # For now, we assume gpt-4o and similar models do.
                    params['model_kwargs'] = {"response_format": {"type": "json_object"}}
                    self.logger.info(f"Initializing OpenAI model {model_name} with JSON mode.")
                model_instance = ChatOpenAI(**params)
            elif provider == 'anthropic':
                model_instance = ChatAnthropic(**params)
            elif provider == 'google':
                model_instance = ChatGoogleGenerativeAI(**params)
            elif provider == 'ollama':
                # Ollama might have different base URL, allow customization if needed
                # Remove unsupported params for Ollama if necessary
                ollama_params = {'model': model_name, 'temperature': 0}
                # Add base_url if specified in config? For now, use default.
                # ollama_params['base_url'] = self.config.get('ollama_base_url', 'http://localhost:11434')
                model_instance = ChatOllama(**ollama_params)
            else:
                self.logger.error(f"Unsupported LLM provider: {provider}")
                return None

            self.logger.info(f"Initialized {provider} model '{model_name}' {'(JSON mode)' if is_json_model else ''} successfully.")
            self.models[cache_key] = model_instance
            return model_instance

        except Exception as e:
            self.logger.error(f"Error initializing {provider} model '{model_name}': {e}")
            # Log specific details if helpful, e.g., connection errors for Ollama
            if provider == 'ollama':
                 self.logger.error("Ensure the Ollama server is running and the model is available locally.")
            return None

    def get_model(self, agent_name=None):
        """
        Gets the appropriate language model based on the agent name specified in the config.
        Falls back to the default model if the agent is not specified or config is missing.
        """
        model_config = self.config.get('default_model', DEFAULT_CONFIG['default_model']) # Start with default

        if agent_name and agent_name in self.config.get('agents', {}):
            agent_specific_config = self.config['agents'][agent_name]
            # Use agent config only if both provider and model_name are present
            if agent_specific_config and 'provider' in agent_specific_config and 'model_name' in agent_specific_config:
                 model_config = agent_specific_config
                 self.logger.info(f"Using model config for agent '{agent_name}': {model_config}")
            else:
                 self.logger.warning(f"Incomplete or invalid model config for agent '{agent_name}'. Falling back to default.")
                 model_config = self.config.get('default_model', DEFAULT_CONFIG['default_model']) # Fallback explicitly
        elif agent_name:
             self.logger.info(f"No specific model config found for agent '{agent_name}'. Using default.")
             model_config = self.config.get('default_model', DEFAULT_CONFIG['default_model']) # Use default
        else:
             self.logger.info("No agent name provided. Using default model config.")
             model_config = self.config.get('default_model', DEFAULT_CONFIG['default_model']) # Use default


        provider = model_config.get('provider')
        model_name = model_config.get('model_name')

        if not provider or not model_name:
            self.logger.error("Invalid model configuration (missing provider or model_name). Cannot get model.")
            # Fallback to hardcoded default if config is severely broken
            provider = DEFAULT_CONFIG['default_model']['provider']
            model_name = DEFAULT_CONFIG['default_model']['model_name']
            self.logger.warning(f"Falling back to hardcoded default: {provider} - {model_name}")

        return self._initialize_model(provider, model_name, is_json_model=False) # Standard model

    def get_json_model(self):
        """Gets the language model configured for JSON output."""
        # Use 'json_model' config if available, otherwise fallback to 'default_model'
        model_config = self.config.get('json_model', self.config.get('default_model', DEFAULT_CONFIG['json_model']))

        provider = model_config.get('provider')
        model_name = model_config.get('model_name')

        if not provider or not model_name:
             self.logger.error("Invalid JSON model configuration. Cannot get JSON model.")
             # Fallback to hardcoded default JSON model
             provider = DEFAULT_CONFIG['json_model']['provider']
             model_name = DEFAULT_CONFIG['json_model']['model_name']
             self.logger.warning(f"Falling back to hardcoded default JSON model: {provider} - {model_name}")

        # Currently, only OpenAI provider explicitly supports JSON mode via parameters
        is_json_mode_provider = (provider == 'openai')

        if not is_json_mode_provider:
            self.logger.warning(f"Provider '{provider}' for JSON model might not explicitly support JSON mode parameter. Using standard initialization for model '{model_name}'. Ensure the model itself can follow JSON instructions.")

        # Initialize specifically for JSON output if provider supports it, otherwise standard init
        return self._initialize_model(provider, model_name, is_json_model=is_json_mode_provider)
