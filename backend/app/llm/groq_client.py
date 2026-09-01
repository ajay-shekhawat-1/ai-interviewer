from functools import lru_cache

from groq import Groq

from app.core.config import get_settings


@lru_cache
def get_groq_client() -> Groq:
    """
    Create and return a cached Groq client.

    The API key is loaded from application settings.
    """

    settings = get_settings()

    return Groq(
        api_key=settings.groq_api_key,
    )


def get_groq_model() -> str:
    """
    Return the configured Groq model ID.
    """

    settings = get_settings()

    return settings.groq_model