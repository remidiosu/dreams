"""Shared Gemini API client with retry logic for transient errors (429, 503)."""

import asyncio
import random
from functools import wraps
from typing import TypeVar, Callable

from google import genai
from google.genai import types

from app.config import settings
from app.logger import logger

T = TypeVar("T")

# Retry settings
MAX_RETRIES = 4
INITIAL_BACKOFF = 1.0
MAX_BACKOFF = 30.0
BACKOFF_MULTIPLIER = 2.0

RETRYABLE_KEYWORDS = [
    "overloaded",
    "503",
    "429",
    "resource exhausted",
    "unavailable",
    "too many requests",
    "rate limit",
    "quota",
    "capacity",
]


def _is_retryable(error: Exception) -> bool:
    error_str = str(error).lower()
    return any(keyword in error_str for keyword in RETRYABLE_KEYWORDS)


def _get_client() -> genai.Client:
    return genai.Client(api_key=settings.gemini_api_key)


def with_retry(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator that adds exponential backoff retry for transient Gemini API errors."""

    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        last_error = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if not _is_retryable(e) or attempt == MAX_RETRIES:
                    raise
                wait = min(
                    INITIAL_BACKOFF * (BACKOFF_MULTIPLIER ** attempt) + random.uniform(0, 1),
                    MAX_BACKOFF,
                )
                logger.warning(
                    f"Gemini API error (attempt {attempt + 1}/{MAX_RETRIES + 1}): {e}. "
                    f"Retrying in {wait:.1f}s..."
                )
                import time
                time.sleep(wait)
        raise last_error  # type: ignore

    return wrapper


async def async_with_retry(func: Callable, *args, **kwargs) -> T:
    """Async retry wrapper for Gemini API calls."""
    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_error = e
            if not _is_retryable(e) or attempt == MAX_RETRIES:
                raise
            wait = min(
                INITIAL_BACKOFF * (BACKOFF_MULTIPLIER ** attempt) + random.uniform(0, 1),
                MAX_BACKOFF,
            )
            logger.warning(
                f"Gemini API error (attempt {attempt + 1}/{MAX_RETRIES + 1}): {e}. "
                f"Retrying in {wait:.1f}s..."
            )
            await asyncio.sleep(wait)
    raise last_error  # type: ignore


def generate_content_with_retry(
    client: genai.Client,
    model: str,
    contents,
    config: types.GenerateContentConfig,
):
    """Call client.models.generate_content with automatic retry on transient errors."""

    @with_retry
    def _call():
        return client.models.generate_content(
            model=model,
            contents=contents,
            config=config,
        )

    return _call()
