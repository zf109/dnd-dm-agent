"""Tests for LLM Engine configuration."""

from config.llm_engine import (
    LLMEngine,
    create_llm_engine,
    get_llm_config,
    get_models_by_provider,
    list_available_models,
)


def test_get_llm_config():
    """Test getting LLM config by name."""
    config = get_llm_config("gemini-2.0-flash")
    assert config.name == "Gemini 2.0 Flash"
    assert config.provider == "google"
    assert config.model_id == "gemini/gemini-2.0-flash-exp"


def test_list_available_models():
    """Test listing all available models."""
    models = list_available_models()
    assert "gemini-2.0-flash" in models
    assert "gpt-4o" in models
    assert "claude-3.5-sonnet" in models


def test_get_models_by_provider():
    """Test getting models by provider."""
    google_models = get_models_by_provider("google")
    assert "gemini-2.0-flash" in google_models
    assert "gemini-1.5-pro" in google_models

    openai_models = get_models_by_provider("openai")
    assert "gpt-4o" in openai_models
    assert "gpt-4o-mini" in openai_models


def test_create_llm_engine():
    """Test creating LLM engine."""
    engine = create_llm_engine("gemini-2.0-flash")
    assert engine.model_name == "gemini-2.0-flash"
    assert engine.config.provider == "google"

    # Test string representation
    assert "Gemini 2.0 Flash" in str(engine)
    assert "google" in str(engine)


def test_llm_engine_with_custom_params():
    """Test LLM engine with custom parameters."""
    engine = LLMEngine("gpt-4o", temperature=0.9, max_tokens=2000)
    assert engine.model_name == "gpt-4o"
    assert "temperature" in engine.kwargs
    assert engine.kwargs["temperature"] == 0.9
