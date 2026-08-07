"""
AI client module for Motivator Bot.

Connects to an Azure AI Foundry deployment through the OpenAI-compatible API.
Configuration comes from environment variables:

- AZURE_AI_ENDPOINT   - Base URL of the Azure AI Foundry OpenAI endpoint
- AZURE_AI_DEPLOYMENT - Deployment name (model) to use
- AZURE_AI_API_KEY    - API key for the endpoint

If any of these are missing, the client reports itself as not configured and
callers should fall back to static content.
"""

import os
from typing import Dict, List, Optional

from openai import AsyncOpenAI

from src.logging_config import get_logger

logger = get_logger(__name__)

_client: Optional[AsyncOpenAI] = None


def is_configured() -> bool:
    """Check whether all required AI environment variables are set."""
    return all(os.getenv(var) for var in (
        'AZURE_AI_ENDPOINT', 'AZURE_AI_DEPLOYMENT', 'AZURE_AI_API_KEY'
    ))


def _get_client() -> AsyncOpenAI:
    """Return a lazily-initialized shared async OpenAI client."""
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            base_url=os.getenv('AZURE_AI_ENDPOINT'),
            api_key=os.getenv('AZURE_AI_API_KEY'),
        )
        logger.info("AI client initialized")
    return _client


async def generate_response(prompt: str, instructions: Optional[str] = None,
                            history: Optional[List[Dict[str, str]]] = None) -> Optional[str]:
    """
    Generate a text response for the given prompt.

    history is an optional list of prior conversation turns, each a dict
    with 'role' ('user' or 'assistant') and 'content'. The prompt is
    appended as the newest user turn.

    Returns the model's text output, or None if the AI is not configured
    or the request fails. Callers must handle the None case with a fallback.
    """
    if not is_configured():
        logger.warning("AI requested but not configured (missing AZURE_AI_* variables)")
        return None

    if history:
        model_input = history + [{'role': 'user', 'content': prompt}]
    else:
        model_input = prompt

    try:
        response = await _get_client().responses.create(
            model=os.getenv('AZURE_AI_DEPLOYMENT'),
            instructions=instructions,
            input=model_input,
        )
        text = response.output_text
        return text.strip() if text else None
    except Exception as e:
        logger.error(f"AI request failed: {e}")
        return None
