import os
import yaml
import openai
import anthropic
from google import genai
from google.genai import types
from abc import ABC, abstractmethod
from typing import Any, Iterator, Dict, Type, List, Optional

from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    HumanMessage,
    ToolMessage,
)
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool
from logger import setup_logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
logger = setup_logger()

# --- Abstract Base Class for Models ---

class AbstractLanguageModel(Runnable, ABC):
    """
    Abstract Base Class for all language model implementations, aligned with LangChain.
    """
    def __init__(self, model_config: Dict[str, Any]):
        self.model_config = model_config
        self.client = None
        self.bound_tools: Optional[List[BaseTool]] = None
        self._initialize_client()

    @abstractmethod
    def _initialize_client(self):
        """Initializes the provider-specific client."""
        pass

    def invoke(self, input: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> AIMessage:
        """
        Sends a single request to the model and returns the complete response.
        """
        messages = input.get("messages", [])
        return self._invoke_internal(messages, self.bound_tools)

    def stream(self, input: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Iterator[AIMessageChunk]:
        """
        Sends a request and streams the response back chunk by chunk.
        """
        messages = input.get("messages", [])
        yield from self._stream_internal(messages, self.bound_tools)

    @abstractmethod
    def _invoke_internal(self, messages: List[BaseMessage], tools: Optional[List[BaseTool]] = None) -> AIMessage:
        pass

    @abstractmethod
    def _stream_internal(self, messages: List[BaseMessage], tools: Optional[List[BaseTool]] = None) -> Iterator[AIMessageChunk]:
        pass

    def with_config(self, config: Dict[str, Any]) -> 'AbstractLanguageModel':
        """
        Allows overriding model parameters for a single call.
        Returns a new instance with the updated configuration.
        """
        new_config = {**self.model_config, **config}
        return self.__class__(model_config=new_config)

    def bind_tools(self, tools: List[BaseTool]) -> 'AbstractLanguageModel':
        """
        Binds tools to the model for function calling.
        Returns a new model instance with the tools bound.
        """
        self.bound_tools = tools
        return self

# --- Concrete Model Implementations ---

class OpenAIModel(AbstractLanguageModel):
    """
    Concrete implementation for OpenAI models.
    """
    def _initialize_client(self):
        api_key_env = self.model_config.get('api_key_env', 'OPENAI_API_KEY')
        api_key = os.getenv(api_key_env)
        if not api_key:
            raise ValueError(f"API key environment variable '{api_key_env}' not set for OpenAI.")
        
        base_url = self.model_config.get('base_url')
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)

    def _invoke_internal(self, messages: List[BaseMessage], tools: Optional[List[BaseTool]] = None) -> AIMessage:
        if not messages:
            return AIMessage(content="")
            
        params = {
            "model": self.model_config.get('model_name'),
            "temperature": self.model_config.get('temperature', 0.2),
            "max_tokens": self.model_config.get('max_tokens', 2048),
            "messages": [msg.dict() for msg in messages],
        }
        
        if tools:
            params["tools"] = [convert_to_openai_tool(tool) for tool in tools]
        
        if 'response_format' in self.model_config:
            params['response_format'] = self.model_config['response_format']

        response = self.client.chat.completions.create(**params)
        message = response.choices[0].message
        return AIMessage(
            content=message.content or "",
            tool_calls=message.tool_calls or [],
            raw_response=response
        )

    def _stream_internal(self, messages: List[BaseMessage], tools: Optional[List[BaseTool]] = None) -> Iterator[AIMessageChunk]:
        if not messages:
            yield AIMessageChunk(content="")
            return

        params = {
            "model": self.model_config.get('model_name'),
            "temperature": self.model_config.get('temperature', 0.2),
            "max_tokens": self.model_config.get('max_tokens', 2048),
            "messages": [msg.dict() for msg in messages],
            "stream": True,
        }
        
        if tools:
            params["tools"] = [convert_to_openai_tool(tool) for tool in tools]

        if 'response_format' in self.model_config:
            params['response_format'] = self.model_config['response_format']

        stream = self.client.chat.completions.create(**params)
        for chunk in stream:
            delta = chunk.choices[0].delta
            yield AIMessageChunk(
                content=delta.content or "",
                tool_call_chunks=delta.tool_calls or [],
                raw_response=chunk
            )

class GoogleModel(AbstractLanguageModel):
    """
    Concrete implementation for Google's Generative AI models, using the new google-genai API.
    """
    def _initialize_client(self):
        api_key_env = self.model_config.get('api_key_env', 'GOOGLE_API_KEY')
        api_key = os.getenv(api_key_env)
        if not api_key:
            raise ValueError(f"API key environment variable '{api_key_env}' not set for Google.")
        
        # The new API uses a client instance, no global configure.
        self.client = genai.Client(api_key=api_key)

    def _invoke_internal(self, messages: List[BaseMessage], tools: Optional[List[BaseTool]] = None) -> AIMessage:
        if not messages:
            return AIMessage(content="")
            
        contents = [msg.content for msg in messages]
        
        generation_config = types.GenerateContentConfig(
            temperature=self.model_config.get('temperature', 0.2),
            max_output_tokens=self.model_config.get('max_tokens', 2048),
        )

        # The new API uses client.models.generate_content
        response = self.client.models.generate_content(
            model=self.model_config.get('model_name'),
            contents=contents,
            config=generation_config
            # Note: The new google-genai SDK handles tools differently.
            # This basic implementation does not yet support tool calling for GoogleModel.
        )
        
        return AIMessage(
            content=response.text,
            raw_response=response
        )

    def _stream_internal(self, messages: List[BaseMessage], tools: Optional[List[BaseTool]] = None) -> Iterator[AIMessageChunk]:
        if not messages:
            yield AIMessageChunk(content="")
            return

        contents = [msg.content for msg in messages]
        
        generation_config = types.GenerateContentConfig(
            temperature=self.model_config.get('temperature', 0.2),
            max_output_tokens=self.model_config.get('max_tokens', 2048),
        )

        # The new API uses client.models.generate_content_stream
        response = self.client.models.generate_content_stream(
            model=self.model_config.get('model_name'),
            contents=contents,
            config=generation_config
        )
        
        for chunk in response:
            yield AIMessageChunk(
                content=chunk.text,
                raw_response=chunk
            )

class AnthropicModel(AbstractLanguageModel):
    """
    Concrete implementation for Anthropic models.
    """
    def _initialize_client(self):
        api_key_env = self.model_config.get('api_key_env', 'ANTHROPIC_API_KEY')
        api_key = os.getenv(api_key_env)
        if not api_key:
            raise ValueError(f"API key environment variable '{api_key_env}' not set for Anthropic.")
        
        self.client = anthropic.Anthropic(api_key=api_key)

    def _invoke_internal(self, messages: List[BaseMessage], tools: Optional[List[BaseTool]] = None) -> AIMessage:
        if not messages:
            return AIMessage(content="")

        response = self.client.messages.create(
            model=self.model_config.get('model_name'),
            max_tokens=self.model_config.get('max_tokens', 2048),
            temperature=self.model_config.get('temperature', 0.2),
            messages=[msg.dict() for msg in messages]
        )
        return AIMessage(
            content=response.content[0].text,
            raw_response=response
        )

    def _stream_internal(self, messages: List[BaseMessage], tools: Optional[List[BaseTool]] = None) -> Iterator[AIMessageChunk]:
        if not messages:
            yield AIMessageChunk(content="")
            return
            
        with self.client.messages.stream(
            model=self.model_config.get('model_name'),
            max_tokens=self.model_config.get('max_tokens', 2048),
            temperature=self.model_config.get('temperature', 0.2),
            messages=[msg.dict() for msg in messages]
        ) as stream:
            for chunk in stream.text_stream:
                yield AIMessageChunk(content=chunk)

# --- Model Factory ---

PROVIDER_MAP: Dict[str, Type[AbstractLanguageModel]] = {
    'openai': OpenAIModel,
    'google': GoogleModel,
    'anthropic': AnthropicModel,
}

class LanguageModelFactory:
    def __init__(self, provider_configs: Dict[str, Any]):
        self._models_cache: Dict[str, AbstractLanguageModel] = {}
        self.provider_configs = provider_configs

    def create_model(self, model_name: str, model_config: Dict[str, Any]) -> AbstractLanguageModel:
        cache_key = model_name
        if cache_key in self._models_cache:
            return self._models_cache[cache_key]

        provider = model_config.get('provider')
        if not provider or provider not in PROVIDER_MAP:
            raise ValueError(f"Unsupported or missing provider: {provider}")

        base_provider_config = self.provider_configs.get(provider, {})
        final_config = {**base_provider_config, **model_config}
        
        ModelClass = PROVIDER_MAP[provider]
        
        try:
            model_instance = ModelClass(model_config=final_config)
            self._models_cache[cache_key] = model_instance
            logger.info(f"Successfully created model '{model_name}' with provider '{provider}'.")
            return model_instance
        except Exception as e:
            logger.error(f"Failed to create model '{model_name}': {e}")
            raise

# --- Language Model Manager ---

class LanguageModelManager:
    def __init__(self, config_path='config.yaml'):
        self.config = self._load_config(config_path)
        provider_configs = self.config.get('provider_configs', {})
        self.model_definitions = self.config.get('models', {})
        self.agent_map = self.config.get('agent_models', {})
        self.factory = LanguageModelFactory(provider_configs)

    def _load_config(self, path: str) -> Dict[str, Any]:
        if not os.path.exists(path):
            logger.warning(f"Configuration file '{path}' not found. Using empty config.")
            return {}
        try:
            with open(path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Successfully loaded configuration from '{path}'.")
                return config or {}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file '{path}': {e}. Using empty config.")
            return {}
        except Exception as e:
            logger.error(f"Error loading configuration file '{path}': {e}. Using empty config.")
            return {}

    def get_model(self, agent_name: str = None) -> AbstractLanguageModel:
        """
        Gets the appropriate language model based on the agent name.
        Falls back to the 'default' model if the agent is not specified or not found.
        """
        if agent_name:
            model_key = self.agent_map.get(agent_name, self.agent_map.get('default', 'default'))
        else:
            model_key = self.agent_map.get('default', 'default')
            
        if not model_key or model_key not in self.model_definitions:
             raise ValueError(f"Model key '{model_key}' not found in model definitions.")

        model_config = self.model_definitions[model_key]
        return self.factory.create_model(model_name=model_key, model_config=model_config)

    def get_json_model(self) -> AbstractLanguageModel:
        """
        Gets the language model specifically configured for JSON output.
        Falls back to 'default_json' or raises an error if not found.
        """
        model_key = self.agent_map.get('json_model', 'default_json')
        
        if not model_key or model_key not in self.model_definitions:
             raise ValueError(f"JSON model key '{model_key}' not found in model definitions.")

        model_config = self.model_definitions[model_key]
        return self.factory.create_model(model_name=model_key, model_config=model_config)
