"""
Chat logic for the Chatbot App.

This module implements the core chat functionality including
prompt construction and LLM invocation. Supports both standalone
mode (LLM only) and integrated mode (augmented with RAG context).
"""

import sys
import logging
from pathlib import Path

# Ensure shared module is importable
_app_root = Path(__file__).resolve().parent.parent
_project_root = _app_root.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from shared.llm_client import LLMClient, LLMResponse  # noqa: E402
from config import config  # noqa: E402
from ai.prompts import build_chat_prompt  # noqa: E402

logger = logging.getLogger(__name__)
import requests

# RAG app endpoint
RAG_APP_URL = "http://localhost:8002/api/query"


def _query_rag_app(message: str) -> str:
    """
    Query the RAG app's /api/query endpoint for relevant context.

    Uses MonitorMiddleware to make the request so that inter-app
    communication is captured by the monitor.

    Args:
        message: The user's message to use as the query.

    Returns:
        A formatted context string from the RAG app, or empty string
        if the request fails or returns no results.
    """
    try:
        response = requests.get(RAG_APP_URL, params={"q": message})
        if response.status_code == 200:
            data = response.json()
            # Extract context chunks from the RAG response
            context_chunks = data.get("context", [])
            answer = data.get("answer", "")

            if context_chunks:
                # Format retrieved chunks as context
                context_parts = []
                for i, chunk in enumerate(context_chunks, 1):
                    context_parts.append(f"[Source {i}]: {chunk}")
                return "\n".join(context_parts)
            elif answer:
                # Fall back to the RAG-generated answer as context
                return f"[RAG Answer]: {answer}"
        else:
            logger.warning(
                "RAG app returned status %d: %s",
                response.status_code,
                response.text[:200]
            )
    except Exception as e:
        logger.warning("Failed to query RAG app: %s", str(e))

    return ""


def generate_response(
    message: str,
    history: list,
    llm_client: LLMClient,
    system_prompt: str = "You are a helpful assistant."
) -> dict:
    """
    Generate a chat response given a message and conversation history.

    When integration_mode is enabled in config, the function first queries
    the RAG app for relevant context and includes it in the prompt to
    augment the LLM response with retrieved knowledge.

    When integration_mode is disabled (standalone mode), the function
    generates responses using only the LLM client.

    Args:
        message: The user's current message.
        history: List of {"role": "user"|"assistant", "content": str}.
        llm_client: Configured LLM client instance.
        system_prompt: System message defining assistant behavior.

    Returns:
        {"response": str, "model": str, "usage": dict}
        In integrated mode, also includes "sources": list[str] if context was retrieved.
    """
    integration_mode = config.get("integration_mode", False)
    context = ""
    sources = []

    # In integrated mode, query the RAG app for relevant context
    if integration_mode:
        context = _query_rag_app(message)
        if context:
            sources = [line for line in context.split("\n") if line.strip()]

    # Build the effective system prompt — augmented with RAG context when available
    if context:
        effective_system_prompt = build_chat_prompt(
            user_message="",
            system_prompt=(
                f"{system_prompt}\n\n"
                f"Use the following retrieved context to help answer the user's question. "
                f"If the context is relevant, incorporate it into your response. "
                f"If it's not relevant, you may ignore it."
            ),
            context=context
        )
    else:
        effective_system_prompt = system_prompt

    # Build messages list from history + new message
    messages = []
    for msg in history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    messages.append({"role": "user", "content": message})

    # Call the LLM client with conversation history
    llm_response: LLMResponse = llm_client.generate_chat(
        messages=messages,
        system_message=effective_system_prompt
    )

    # TODO: Add streaming support
    # TODO: Implement token counting

    result = {
        "response": llm_response.text,
        "model": llm_response.model,
        "usage": llm_response.usage
    }

    # Include sources when in integrated mode and context was retrieved
    if integration_mode and sources:
        result["sources"] = sources

    return result
