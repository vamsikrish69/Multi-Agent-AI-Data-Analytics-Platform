from functools import lru_cache

from langchain_core.language_models.chat_models import BaseChatModel

from ai_data_agent.config.settings import get_settings


class UnsupportedProviderError(Exception):
    """Raised when LLM_PROVIDER in settings doesn't match a known provider."""


@lru_cache
def get_chat_model() -> BaseChatModel:
    """Return a chat model instance based on the configured LLM_PROVIDER.

    Every agent should call this function rather than importing a
    specific provider (Ollama, Anthropic, etc.) directly. Swapping
    providers later means changing .env, not this function's callers.
    """
    settings = get_settings()

    if settings.llm_provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=settings.llm_model_name,
            base_url=settings.ollama_base_url,
            temperature=0,
        )

    raise UnsupportedProviderError(
        f"Unknown LLM_PROVIDER '{settings.llm_provider}'. "
        f"Supported providers: ollama"
    )