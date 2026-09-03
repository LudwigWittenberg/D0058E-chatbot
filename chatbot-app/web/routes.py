"""
Route definitions for the Chatbot App — SERVER-SIDE MEMORY VERSION.

=== LAB 1, TASK 1.3 ===

This file replaces the original chatbot-app/web/routes.py.
The key change: conversation history is now managed on the SERVER
using the ConversationMemory class, instead of being accumulated
on the client (JavaScript) and sent with each request.

HOW TO USE:
    1. Back up the original:  cp chatbot-app/web/routes.py chatbot-app/web/routes_old.py
    2. Copy this file:        cp student_test/lab1_server_memory/routes.py chatbot-app/web/routes.py
    3. Flask will auto-restart (debug mode)

WHAT CHANGED (compared to routes_old.py):
    - Added: import of ConversationMemory
    - Added: _memory = ConversationMemory(max_messages=50) as module-level state
    - Changed: /chat endpoint no longer reads history from client request
    - Changed: /chat endpoint stores user + assistant messages in _memory
    - Changed: /chat response includes memory_stats for monitoring
    - Added: GET /api/memory — shows current memory state (message count, tokens)
    - Added: POST /api/memory/clear — resets conversation memory
"""

import sys
from pathlib import Path

from flask import Blueprint, render_template, request, jsonify

# Ensure shared module is importable
_app_root = Path(__file__).resolve().parent.parent
_project_root = _app_root.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from shared.llm_client import LLMClient, LLMConfig, LLMBackend, LLMClientError  # noqa: E402

# === NEW: Import ConversationMemory for server-side history management ===
from ai.memory import ConversationMemory  # noqa: E402

bp = Blueprint("main", __name__)

# === NEW: Server-side conversation memory ===
# This replaces the client-side history array in chat.js.
# All messages (user + assistant) are stored here.
# When max_messages is exceeded, oldest messages are dropped.
# Try changing max_messages to 10 to see forgetting happen faster.
_memory = ConversationMemory(max_messages=10)
# _memory = ConversationMemory(max_messages=50)


# ---------------------------------------------------------------------------
# Valid configuration keys (unchanged from original)
# ---------------------------------------------------------------------------
_VALID_CONFIG_KEYS = {
    "llm_backend": str,
    "llm_model": str,
    "api_key_openai": str,
    "api_key_gemini": str,
    "ollama_base_url": str,
    "temperature": float,
    "max_tokens": int,
    "system_prompt": str,
    "chunk_size": int,
    "chunk_overlap": int,
    "top_k": int,
    "embedding_model": str,
    "crew_process_type": str,
    "max_iterations": int,
    "integration_mode": bool,
}

_VALID_BACKENDS = {"ollama", "openai", "gemini"}


# ---------------------------------------------------------------------------
# Page routes (unchanged)
# ---------------------------------------------------------------------------


@bp.route("/")
def index():
    """Render the main chat interface."""
    return render_template("index.html")


@bp.route("/settings")
def settings():
    """Render the configuration settings page."""
    return render_template("settings.html")


# ---------------------------------------------------------------------------
# Persona endpoint (unchanged)
# ---------------------------------------------------------------------------


@bp.route("/api/personas", methods=["GET"])
def list_personas_route():
    """
    Return the list of available persona names.

    Returns JSON: {"personas": ["default", "helpful", "creative", ...]}
    """
    from ai.prompts import list_personas
    return jsonify({"personas": list_personas()})


# ---------------------------------------------------------------------------
# === NEW: Memory monitoring endpoints ===
# These let you observe how context grows with each message.
# ---------------------------------------------------------------------------


@bp.route("/api/memory", methods=["GET"])
def get_memory_status():
    """
    Return current memory state for monitoring.

    Shows:
    - How many messages are stored
    - Estimated token count (1 token ≈ 4 characters)
    - What percentage of the 2048-token budget is used
    - A preview of each stored message

    Use this to watch context grow as you chat!
    """
    history = _memory.get_history()
    total_chars = sum(len(m["content"]) for m in history)
    # Token estimate: ~1 token per 3 characters for Llama tokenizer
    estimated_tokens = (total_chars * 10) // 30  # ~3 chars per token for Llama

    return jsonify({
        "message_count": len(history),
        "max_messages": _memory.max_messages,
        "total_characters": total_chars,
        "estimated_tokens": estimated_tokens,
        # Assuming 2048-token context window (set via num_ctx)
        "context_budget": 4096,
        "budget_used_pct": round(estimated_tokens / 4096 * 100, 1),
        # Preview of each message (truncated for readability)
        "messages": [
            {
                "role": m["role"],
                "content": m["content"][:80] + ("..." if len(m["content"]) > 80 else ""),
                "chars": len(m["content"]),
                "est_tokens": (len(m["content"]) * 10) // 30,
            }
            for m in history
        ],
    })


@bp.route("/api/memory/clear", methods=["POST"])
def clear_memory():
    """
    Clear all conversation memory.

    Use this to start a fresh conversation without restarting the app.
    Call before running the test script to get clean results.
    """
    _memory.clear()
    return jsonify({"status": "ok", "message": "Memory cleared"})


# ---------------------------------------------------------------------------
# === CHANGED: Chat endpoint — now uses server-side memory ===
# ---------------------------------------------------------------------------


@bp.route("/chat", methods=["POST"])
def chat():
    """
    Handle a chat message using SERVER-SIDE memory.

    === KEY DIFFERENCE FROM ORIGINAL ===
    Original: client sends {"message": str, "history": [...all messages...]}
    This version: client sends {"message": str} — server manages history

    The flow:
    1. Client sends only the new message (no history)
    2. Server retrieves history from ConversationMemory
    3. Server sends history + new message to the LLM
    4. Server stores BOTH user message AND assistant response in memory
    5. Server returns response + memory_stats for monitoring

    Accepts JSON: {"message": str, "persona": str (optional)}
    Returns JSON: {"response": str, "model": str, "usage": dict, "memory_stats": dict}
    """
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    message = data["message"]
    persona = data.get("persona", None)
    # NOTE: We intentionally ignore data.get("history") — server manages it

    try:
        from ai.chat import generate_response
        from ai.prompts import get_system_prompt
        from config import config
        from ai.models import create_client

        backend = config.get("llm_backend", "ollama")
        llm_client = create_client(backend, config.get_all())

        # Use persona-specific prompt if provided, otherwise fall back to config
        if persona:
            system_prompt = get_system_prompt(persona)
        else:
            system_prompt = config.get("system_prompt", "You are a helpful assistant.")

        # === CHANGED: Get history from server-side memory (NOT from client) ===
        history = _memory.get_history()

        # Call the LLM with the full history + new message
        result = generate_response(
            message=message,
            history=history,
            llm_client=llm_client,
            system_prompt=system_prompt,
        )

        # === NEW: Store both user message and assistant response in memory ===
        # Each turn adds 2 messages — this is why context fills up fast!
        _memory.add_message("user", message)
        _memory.add_message("assistant", result["response"])

        # === NEW: Include memory stats in response for monitoring ===
        # The chat.js displays these below each response
        current_history = _memory.get_history()
        total_chars = sum(len(m["content"]) for m in current_history)
        estimated_tokens = (total_chars * 10) // 30  # ~3 chars per token for Llama

        result["memory_stats"] = {
            "messages_in_memory": len(current_history),
            "max_messages": _memory.max_messages,
            "estimated_tokens": estimated_tokens,
            "context_budget": 4096,
            "budget_used_pct": round(estimated_tokens / 4096 * 100, 1),
        }

        return jsonify(result)

    except (NotImplementedError, ImportError):
        return jsonify({
            "response": "AI module not yet implemented. See ai/chat.py",
            "model": "placeholder",
            "usage": {},
        })
    except Exception as e:
        return jsonify({
            "response": f"Error: {str(e)}",
            "model": "error",
            "usage": {},
        })


# ---------------------------------------------------------------------------
# API generate endpoint (unchanged — used for inter-app communication)
# ---------------------------------------------------------------------------


@bp.route("/api/generate", methods=["POST"])
def api_generate():
    """
    API endpoint for generating a chat response (inter-app use).
    This endpoint is NOT affected by server-side memory — it uses
    whatever history the caller provides (for integration mode).

    Accepts JSON: {"prompt": str, "system_prompt": str, "history": list}
    Returns JSON: {"response": str, "model": str, "usage": dict}
    """
    data = request.get_json()
    if not data or "prompt" not in data:
        return jsonify({"error": "Missing 'prompt' field"}), 400

    prompt = data["prompt"]
    system_prompt = data.get("system_prompt", "You are a helpful assistant.")
    history = data.get("history", [])

    try:
        from ai.chat import generate_response
        from config import config
        from ai.models import create_client

        backend = config.get("llm_backend", "ollama")
        llm_client = create_client(backend, config.get_all())

        result = generate_response(
            message=prompt,
            history=history,
            llm_client=llm_client,
            system_prompt=system_prompt,
        )
        return jsonify(result)

    except (NotImplementedError, ImportError):
        return jsonify({
            "response": "AI module not yet implemented. See ai/chat.py",
            "model": "placeholder",
            "usage": {},
        })
    except Exception as e:
        return jsonify({
            "response": f"Error: {str(e)}",
            "model": "error",
            "usage": {},
        })


# ---------------------------------------------------------------------------
# Configuration API routes (unchanged from original)
# ---------------------------------------------------------------------------


@bp.route("/api/config", methods=["GET"])
def get_config():
    """Return the current application configuration as JSON."""
    from config import config
    return jsonify(config.get_all())


@bp.route("/api/config", methods=["POST"])
def update_config():
    """Accept partial configuration updates, validate, and persist."""
    from config import config

    data = request.get_json()
    if data is None or not isinstance(data, dict):
        return jsonify({"status": "error", "message": "Request body must be a JSON object"}), 400

    errors = []
    updated_keys = []

    for key, value in data.items():
        if key not in _VALID_CONFIG_KEYS:
            errors.append(f"Unknown configuration key: '{key}'")
            continue
        if key == "llm_backend" and value not in _VALID_BACKENDS:
            errors.append(f"Invalid llm_backend '{value}'. Must be one of: {', '.join(_VALID_BACKENDS)}")
            continue
        if key == "temperature":
            try:
                val = float(value)
                if val < 0.0 or val > 2.0:
                    errors.append("temperature must be between 0.0 and 2.0")
                    continue
            except (ValueError, TypeError):
                errors.append("temperature must be a number")
                continue
        if key == "max_tokens":
            try:
                val = int(value)
                if val < 1:
                    errors.append("max_tokens must be a positive integer")
                    continue
            except (ValueError, TypeError):
                errors.append("max_tokens must be an integer")
                continue

        config.set(key, value)
        updated_keys.append(key)

    if errors:
        return jsonify({"status": "error", "message": "; ".join(errors), "updated": updated_keys}), 400
    return jsonify({"status": "ok", "updated": updated_keys})


@bp.route("/api/config/test-connection", methods=["POST"])
def test_connection():
    """Test LLM backend connectivity and return status."""
    from config import config

    data = request.get_json() or {}
    backend_name = data.get("backend", config.get("llm_backend", "ollama"))
    model_name = data.get("model", config.get("llm_model", "Llama-3.2-3B-Instruct-Q4_K_M"))

    if "api_key" in data:
        api_key = data["api_key"]
    elif backend_name == "openai":
        api_key = config.get("api_key_openai")
    elif backend_name == "gemini":
        api_key = config.get("api_key_gemini")
    else:
        api_key = None

    base_url = data.get("base_url", config.get("ollama_base_url", "http://localhost:11434"))

    backend_map = {"ollama": LLMBackend.OLLAMA, "openai": LLMBackend.OPENAI, "gemini": LLMBackend.GEMINI}
    backend_enum = backend_map.get(backend_name)
    if backend_enum is None:
        return jsonify({
            "status": "error", "backend": backend_name, "model": model_name,
            "message": f"Unknown backend '{backend_name}'",
        }), 400

    try:
        llm_config = LLMConfig(backend=backend_enum, model_name=model_name, api_key=api_key, base_url=base_url)
        client = LLMClient(llm_config)
        result = client.test_connection()
        return jsonify(result)
    except LLMClientError as e:
        return jsonify({"status": "error", "backend": backend_name, "model": model_name, "message": e.reason})
    except Exception as e:
        return jsonify({"status": "error", "backend": backend_name, "model": model_name, "message": str(e)})
