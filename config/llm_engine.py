"""LLM Engine configuration for DnD DM Agent.

Based on common patterns from popular agent frameworks like HuggingFace Transformers,
LangChain, and CrewAI for configuring multiple LLM backends.
"""

import os
from typing import Dict, Optional

from google.adk.models.lite_llm import LiteLlm
from pydantic import BaseModel


class LLMConfig(BaseModel):
    """Configuration for LLM model providers."""

    name: str
    provider: str
    model_id: str
    description: str
    requires_api_key: bool = True
    api_key_env_var: str = ""
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None


class LLMEngine:
    """
    LLM Engine abstraction following patterns from popular agent frameworks.
    Provides unified interface to multiple LLM providers via LiteLLM.
    """

    def __init__(self, model_name: str = "gemini-2.0-flash", **kwargs):
        self.config = get_llm_config(model_name)
        self.model_name = model_name
        self.kwargs = kwargs

        # Check for required API key
        if self.config.requires_api_key:
            if not os.getenv(self.config.api_key_env_var):
                print(f"Warning: {self.config.api_key_env_var} not found in environment")

    def create_model(self) -> LiteLlm:
        """Create LiteLLM model instance with configuration."""
        model_kwargs = {}

        # Add optional parameters if specified
        if self.config.max_tokens:
            model_kwargs["max_tokens"] = self.config.max_tokens
        if self.config.temperature:
            model_kwargs["temperature"] = self.config.temperature

        # Merge with any additional kwargs
        model_kwargs.update(self.kwargs)

        return LiteLlm(model=self.config.model_id, **model_kwargs)

    def __str__(self) -> str:
        return f"LLMEngine({self.config.name} - {self.config.provider})"


# Available model configurations
LLM_CONFIGS: Dict[str, LLMConfig] = {
    # Google Gemini models
    "gemini-2.0-flash": LLMConfig(
        name="Gemini 2.0 Flash",
        provider="google",
        model_id="gemini/gemini-2.0-flash-exp",
        description="Latest Gemini model with fast inference",
        requires_api_key=True,
        api_key_env_var="GOOGLE_API_KEY",
        max_tokens=8192,
        temperature=0.7,
    ),
    "gemini-1.5-pro": LLMConfig(
        name="Gemini 1.5 Pro",
        provider="google",
        model_id="gemini/gemini-1.5-pro",
        description="High-quality reasoning model",
        requires_api_key=True,
        api_key_env_var="GOOGLE_API_KEY",
        max_tokens=8192,
        temperature=0.7,
    ),
    # OpenAI models
    "gpt-4o": LLMConfig(
        name="GPT-4o",
        provider="openai",
        model_id="openai/gpt-4o",
        description="OpenAI's latest multimodal model",
        requires_api_key=True,
        api_key_env_var="OPENAI_API_KEY",
        max_tokens=4096,
        temperature=0.7,
    ),
    "gpt-4o-mini": LLMConfig(
        name="GPT-4o Mini",
        provider="openai",
        model_id="openai/gpt-4o-mini",
        description="Faster, cheaper version of GPT-4o",
        requires_api_key=True,
        api_key_env_var="OPENAI_API_KEY",
        max_tokens=4096,
        temperature=0.7,
    ),
    # Anthropic models
    "claude-3.5-sonnet": LLMConfig(
        name="Claude 3.5 Sonnet",
        provider="anthropic",
        model_id="anthropic/claude-3-5-sonnet-20241022",
        description="Anthropic's latest reasoning model",
        requires_api_key=True,
        api_key_env_var="ANTHROPIC_API_KEY",
        max_tokens=4096,
        temperature=0.7,
    ),
    "claude-3.5-haiku": LLMConfig(
        name="Claude 3.5 Haiku",
        provider="anthropic",
        model_id="anthropic/claude-3-5-haiku-20241022",
        description="Fast and efficient Claude model",
        requires_api_key=True,
        api_key_env_var="ANTHROPIC_API_KEY",
        max_tokens=4096,
        temperature=0.7,
    ),
    # Other providers
    "mistral-large": LLMConfig(
        name="Mistral Large",
        provider="mistral",
        model_id="mistral/mistral-large-latest",
        description="Mistral's largest model",
        requires_api_key=True,
        api_key_env_var="MISTRAL_API_KEY",
        max_tokens=4096,
        temperature=0.7,
    ),
    "llama-3.1-70b": LLMConfig(
        name="Llama 3.1 70B",
        provider="groq",
        model_id="groq/llama-3.1-70b-versatile",
        description="Meta's Llama model via Groq",
        requires_api_key=True,
        api_key_env_var="GROQ_API_KEY",
        max_tokens=4096,
        temperature=0.7,
    ),
}


def get_llm_config(model_name: str) -> LLMConfig:
    """Get LLM configuration by name."""
    if model_name not in LLM_CONFIGS:
        raise ValueError(f"Unknown model: {model_name}. Available models: {list(LLM_CONFIGS.keys())}")
    return LLM_CONFIGS[model_name]


def list_available_models() -> Dict[str, str]:
    """List all available models with descriptions."""
    return {name: config.description for name, config in LLM_CONFIGS.items()}


def get_models_by_provider(provider: str) -> Dict[str, LLMConfig]:
    """Get all models for a specific provider."""
    return {name: config for name, config in LLM_CONFIGS.items() if config.provider == provider}


def create_llm_engine(model_name: str = "gemini-2.0-flash", **kwargs) -> LLMEngine:
    """Factory function to create LLM engine instance."""
    return LLMEngine(model_name=model_name, **kwargs)
