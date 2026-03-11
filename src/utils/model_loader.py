import asyncio
import sys
import os
import json
from dotenv import load_dotenv
from src.utils.config_loader import load_config
from langchain_groq import ChatGroq
from langchain_google_genai import  GoogleGenerativeAIEmbeddings,ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_ollama import ChatOllama, OllamaEmbeddings
from src.logger import GLOBAL_LOGGER as log
from src.exceptions.custom_exception import CustomException


class ApiKeyManager:
    """
    Manages API keys for different LLM providers.
    """
    def __init__(self):
        load_dotenv()

        self.api_keys = {
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
            "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
            "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        }

        log.info("Initialized ApiKeyManager")

        # Log loaded key statuses without exposing secrets
        for key, value in self.api_keys.items():
            if value:
                log.info(f"Loaded successfully API key for {key}")
            else:
                log.warning(f"No API key found for {key}")
        
    def get_api_key(self, provider: str):
        """
        Get the API key for a given provider.

        Args:
            provider: The name of the provider to get the API key for.
        
        Returns:
            The API key for the given provider.
        """
        return self.api_keys.get(provider)


class ModelLoader:
    """
    Loads embeddings and LLMs dynamically based on YAML configuration and environment settings.
    """
    def __init__(self):
        """
        Initialize the ModelLoader with configuration and API key manager.
        """
        try:
            self.api_key_manager = ApiKeyManager()
            self.config = load_config()
            log.info("YAML configuration loaded successfully", config_keys=list(self.config.keys()))
        except Exception as e:
            log.error("Error while initializing ModelLoader", error=str(e))
            raise CustomException(f"Failed to initialize ModelLoader: {str(e)}")
    
    def _get_required_api_key(self, key_name: str, provider: str) -> str:
        """
        Get and validate an API key exists.
        
        Args:
            key_name: The API key name (e.g., "GOOGLE_API_KEY")
            provider: The provider name for error messaging
            
        Returns:
            The API key string
            
        Raises:
            CustomException: If the API key is missing
        """
        api_key = self.api_key_manager.get_api_key(key_name)
        if not api_key:
            log.error("Missing API key", key_name=key_name, provider=provider)
            raise CustomException(f"Missing API key '{key_name}' for provider '{provider}'")
        return api_key
    
    # ----------------------------------------------------------------------
    # Embedding Loader
    # ----------------------------------------------------------------------
    def load_embedding_model(self):
        """
        Loads the embedding model based on the configured model provider

        Supported providers:
         - google
         - openai
         - ollama(nomic-embed-text)

        Returns:
            The embedding model
        """
        try:
            embedding_block = self.config["embedding_model"]
            provider = os.getenv("EMBEDDING_PROVIDER","ollama")

            if provider not in embedding_block:
                log.error("Embedding provider not found in configuration", provider=provider)
                raise CustomException(f"Embedding provider {provider} not found in configuration")
            
            embedding_provider = embedding_block[provider]
            model_name = embedding_provider.get("model_name")

    
            if provider == "google":
                embedding = GoogleGenerativeAIEmbeddings(
                    model=model_name,
                    api_key=self._get_required_api_key("GOOGLE_API_KEY", provider),
                )
            elif provider == "openai":
                embedding = OpenAIEmbeddings(
                    model=model_name,
                    api_key=self._get_required_api_key("OPENAI_API_KEY", provider),
                )
            elif provider == "ollama":
                embedding = OllamaEmbeddings(
                    model=model_name,
                )
            else:
                log.error("Unsupported embedding provider", provider=provider)
                raise CustomException(f"Unsupported embedding provider: {provider}")
            
            log.info("Embedding model loaded successfully", provider=provider, model_name=model_name)
            return embedding

        except Exception as e:
            log.error("Error while loading embedding model", error=str(e))
            raise CustomException("Failed to load embedding model", sys)
    # ----------------------------------------------------------------------
    # LLM Loader
    # ----------------------------------------------------------------------
    
    def load_llm(self):
        """
        Loads the LLM model based on the configured model provider

        Supported providers:
        - groq
        - google
        - openai
        - ollama

        Returns:
            The LLM model
        """
        try:
            llm_block = self.config["llm"]
            provider = os.getenv("LLM_PROVIDER","ollama")

            if provider not in llm_block:
                log.error("LLM provider not found in configuration", provider=provider)
                raise CustomException(f"LLM provider {provider} not found in configuration")
            
            llm_provider = llm_block[provider]
            model_name = llm_provider.get("model_name")
            temperature = llm_provider.get("temperature", 0.2)
            max_tokens = llm_provider.get("max_output_tokens", 2048)

            log.info("Loading LLM model", provider=provider, model_name=model_name)

            if provider == "google":
                llm = ChatGoogleGenerativeAI(
                    model=model_name,
                    api_key=self._get_required_api_key("GOOGLE_API_KEY", provider),
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            elif provider == "openai":
                llm = ChatOpenAI(
                    model=model_name,
                    api_key=self._get_required_api_key("OPENAI_API_KEY", provider),
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            elif provider == "groq":
                llm = ChatGroq(
                    model=model_name,
                    api_key=self._get_required_api_key("GROQ_API_KEY", provider),
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            elif provider == "ollama":
                llm = ChatOllama(
                    model=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

            else:
                log.error("Unsupported LLM provider", provider=provider)
                raise CustomException(f"Unsupported LLM provider: {provider}")
            
            log.info("LLM model loaded successfully", provider=provider, model_name=model_name)
            return llm

        except Exception as e:
            log.error("Error while loading LLM model", error=str(e))
            raise CustomException("Failed to load LLM model", sys)


# test the model loader
if __name__ == "__main__":
    model_loader = ModelLoader()
    embedding_model = model_loader.load_embedding_model()
    llm_model = model_loader.load_llm()
    print(embedding_model)
    print(llm_model)
    print(llm_model.invoke([{"role": "user", "content": "Hello, how are you?"}]))
