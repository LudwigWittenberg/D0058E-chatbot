"""
Route definitions for the Agents App.

This module defines all Flask routes (web pages and API endpoints)
for the agents application. Routes are registered as a Blueprint.
"""

import sys
import threading
import uuid
from pathlib import Path

from flask import Blueprint, render_template, request, jsonify

# Ensure shared module is importable
_app_root = Path(__file__).resolve().parent.parent
_project_root = _app_root.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from shared.llm_client import LLMClient, LLMConfig, LLMBackend, LLMClientError  # noqa: E402

bp = Blueprint("main", __name__)

# Valid configuration keys and their expected types for validation
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

# In-memory execution state (keyed by execution_id)
_executions = {}
_executions_lock = threading.Lock()


@bp.route("/")
def index():
    """Render the agents dashboard."""
    # Load agent and task definitions for display
    try:
        from ai.agents import get_agents
        from ai.tasks import get_tasks

        agents = get_agents()
        tasks = get_tasks()

        agents_data = []
        if agents:
            agents_data = [
                {
                    "role": a.role,
                    "goal": a.goal,
                    "backstory": a.backstory,
                    "tools": a.tools,
                }
                for a in agents
            ]

        tasks_data = []
        if tasks:
            tasks_data = [
                {
                    "description": t.description,
                    "expected_output": t.expected_output,
                    "agent_role": t.agent_role,
                }
                for t in tasks
            ]
    except (NotImplementedError, ImportError, TypeError):
        agents_data = []
        tasks_data = []

    return render_template("index.html", agents=agents_data, tasks=tasks_data)


@bp.route("/api/agents")
def api_agents():
    """Return current agent definitions as JSON (re-reads from ai/agents.py)."""
    try:
        # Force reimport to pick up code changes
        import importlib
        import ai.agents as agents_module
        importlib.reload(agents_module)
        from ai.agents import get_agents

        agents = get_agents()
        agents_data = [
            {
                "role": a.role,
                "goal": a.goal,
                "backstory": a.backstory,
                "tools": a.tools,
            }
            for a in agents
        ] if agents else []

        return jsonify({"agents": agents_data})
    except Exception as e:
        return jsonify({"agents": [], "error": str(e)}), 500


@bp.route("/api/tasks")
def api_tasks():
    """Return current task definitions as JSON (re-reads from ai/tasks.py)."""
    try:
        import importlib
        import ai.tasks as tasks_module
        importlib.reload(tasks_module)
        from ai.tasks import get_tasks

        tasks = get_tasks()
        tasks_data = [
            {
                "description": t.description,
                "expected_output": t.expected_output,
                "agent_role": t.agent_role,
            }
            for t in tasks
        ] if tasks else []

        return jsonify({"tasks": tasks_data})
    except Exception as e:
        return jsonify({"tasks": [], "error": str(e)}), 500


@bp.route("/settings")
def settings():
    """Render the configuration settings page."""
    return render_template("settings.html")


@bp.route("/execute", methods=["POST"])
def execute():
    """
    Start a crew execution (init + run in one call, legacy).

    Accepts JSON: {"topic": str} (optional topic/input for the crew)
    Returns JSON: {"execution_id": str, "status": "started"}
    """
    data = request.get_json() or {}
    topic = data.get("topic", "AI and machine learning trends")

    execution_id = str(uuid.uuid4())

    with _executions_lock:
        _executions[execution_id] = {
            "status": "running",
            "logs": [],
            "result": None,
            "error": None,
        }

    # Run crew execution in a background thread
    thread = threading.Thread(
        target=_run_crew_full,
        args=(execution_id, topic),
        daemon=True,
    )
    thread.start()

    return jsonify({"execution_id": execution_id, "status": "started"})


# Global crew instance (initialized via /api/crew/init)
_initialized_crew = None
_crew_lock = threading.Lock()


@bp.route("/api/crew/init", methods=["POST"])
def crew_init():
    """
    Initialize the crew pipeline (steps 1-5) without executing.

    Loads agents, loads tasks, matches them, assembles the Crew.
    Returns JSON: {"status": "ok"|"error", "logs": list, "error": str|null}
    """
    global _initialized_crew

    logs = []

    def _add_log(msg):
        logs.append(msg)

    # Clear previous response log files
    import glob
    import os
    for f in glob.glob("/tmp/crew_response_*.txt"):
        try:
            os.remove(f)
        except Exception:
            pass

    try:
        from ai.crew import initialize_crew

        crew = initialize_crew(on_progress=_add_log)

        with _crew_lock:
            _initialized_crew = crew

        return jsonify({"status": "ok", "logs": logs})

    except Exception as e:
        logs.append(f"Error: {str(e)}")
        return jsonify({"status": "error", "logs": logs, "error": str(e)}), 500


@bp.route("/api/crew/run", methods=["POST"])
def crew_run():
    """
    Execute the initialized crew on a topic (step 6).

    Requires crew to be initialized first via /api/crew/init.
    Accepts JSON: {"topic": str}
    Returns JSON: {"execution_id": str, "status": "started"}
    """
    global _initialized_crew

    with _crew_lock:
        if _initialized_crew is None:
            return jsonify({
                "error": "Crew not initialized. Call /api/crew/init first."
            }), 400

    data = request.get_json() or {}
    topic = data.get("topic", "AI and machine learning trends")

    execution_id = str(uuid.uuid4())

    with _executions_lock:
        _executions[execution_id] = {
            "status": "running",
            "logs": [],
            "result": None,
            "error": None,
        }

    thread = threading.Thread(
        target=_run_crew_execute,
        args=(execution_id, topic),
        daemon=True,
    )
    thread.start()

    return jsonify({"execution_id": execution_id, "status": "started"})


@bp.route("/api/crew/status", methods=["GET"])
def crew_status():
    """Check if crew is initialized."""
    with _crew_lock:
        initialized = _initialized_crew is not None
    return jsonify({"initialized": initialized})


@bp.route("/api/crew/check-tools", methods=["GET"])
def crew_check_tools():
    """Check if custom tools (WordCountTool) are implemented."""
    try:
        from ai.tools import WordCountTool
        # Try to instantiate it
        tool = WordCountTool()
        return jsonify({"tools_available": True, "tool_name": tool.name})
    except (ImportError, AttributeError, NotImplementedError):
        return jsonify({"tools_available": False})


@bp.route("/api/crew/responses", methods=["GET"])
def crew_responses():
    """Return all saved LLM response files in chronological order."""
    import glob
    import os

    files = sorted(glob.glob("/tmp/crew_response_*.txt"))
    responses = []
    for filepath in files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            filename = os.path.basename(filepath)
            responses.append({"filename": filename, "content": content})
        except Exception:
            continue

    return jsonify({"responses": responses})


@bp.route("/api/crew/responses/clear", methods=["POST"])
def crew_responses_clear():
    """Delete all saved LLM response files."""
    import glob
    import os

    files = glob.glob("/tmp/crew_response_*.txt")
    for f in files:
        try:
            os.remove(f)
        except Exception:
            pass
    return jsonify({"status": "ok", "deleted": len(files)})


@bp.route("/status", methods=["GET"])
def status():
    """
    Get crew execution progress.

    Query params: ?execution_id=<id>
    Returns JSON: {"status": str, "logs": list, "result": str|null, "error": str|null}
    """
    execution_id = request.args.get("execution_id", "").strip()

    if not execution_id:
        return jsonify({"error": "Missing 'execution_id' query parameter"}), 400

    with _executions_lock:
        execution = _executions.get(execution_id)

    if execution is None:
        return jsonify({"error": "Execution not found"}), 404

    return jsonify({
        "status": execution["status"],
        "logs": execution["logs"],
        "result": execution["result"],
        "error": execution["error"],
    })


def _run_crew_full(execution_id: str, topic: str) -> None:
    """Execute the full pipeline (init + run) in a background thread."""
    def _add_log(message: str):
        with _executions_lock:
            _executions[execution_id]["logs"].append(message)

    try:
        _add_log("Initializing crew execution...")
        from ai.crew import run_crew_pipeline

        result = run_crew_pipeline(topic=topic, on_progress=_add_log)

        with _executions_lock:
            _executions[execution_id]["status"] = "completed"
            _executions[execution_id]["result"] = result.get("result", "")

    except NotImplementedError as e:
        _add_log(f"AI module not yet implemented: {str(e)}")
        with _executions_lock:
            _executions[execution_id]["status"] = "error"
            _executions[execution_id]["error"] = (
                "AI module not yet implemented. See ai/ folder for TODO items."
            )

    except Exception as e:
        _add_log(f"Error: {str(e)}")
        with _executions_lock:
            _executions[execution_id]["status"] = "error"
            _executions[execution_id]["error"] = str(e)


def _run_crew_execute(execution_id: str, topic: str) -> None:
    """Execute an already-initialized crew in a background thread."""
    global _initialized_crew

    def _add_log(message: str):
        with _executions_lock:
            _executions[execution_id]["logs"].append(message)

    try:
        from ai.crew import run_crew

        with _crew_lock:
            crew = _initialized_crew

        if crew is None:
            raise RuntimeError("Crew not initialized")

        result = run_crew(crew, topic, on_progress=_add_log)

        with _executions_lock:
            _executions[execution_id]["status"] = "completed"
            _executions[execution_id]["result"] = result.get("result", "")

    except Exception as e:
        _add_log(f"Error: {str(e)}")
        with _executions_lock:
            _executions[execution_id]["status"] = "error"
            _executions[execution_id]["error"] = str(e)


# -------------------------------------------------------------------------
# Configuration API routes
# -------------------------------------------------------------------------


@bp.route("/api/config", methods=["GET"])
def get_config():
    """
    Return the current application configuration as JSON.

    Returns JSON: full config dictionary from ConfigManager.
    """
    from config import config

    return jsonify(config.get_all())


@bp.route("/api/config", methods=["POST"])
def update_config():
    """
    Accept partial configuration updates, validate, and persist.

    Accepts JSON: {"key": value, ...} with any valid config keys.
    Returns JSON: {"status": "ok", "updated": list[str]} on success,
                  or {"status": "error", "message": str} on failure.
    """
    from config import config

    data = request.get_json()
    if data is None or not isinstance(data, dict):
        return jsonify({"status": "error", "message": "Request body must be a JSON object"}), 400

    errors = []
    updated_keys = []

    for key, value in data.items():
        # Validate key is recognized
        if key not in _VALID_CONFIG_KEYS:
            errors.append(f"Unknown configuration key: '{key}'")
            continue

        # Validate llm_backend value
        if key == "llm_backend" and value not in _VALID_BACKENDS:
            errors.append(
                f"Invalid llm_backend '{value}'. Must be one of: {', '.join(_VALID_BACKENDS)}"
            )
            continue

        # Validate numeric ranges
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

        if key == "chunk_size":
            try:
                val = int(value)
                if val < 1:
                    errors.append("chunk_size must be a positive integer")
                    continue
            except (ValueError, TypeError):
                errors.append("chunk_size must be an integer")
                continue

        if key == "chunk_overlap":
            try:
                val = int(value)
                if val < 0:
                    errors.append("chunk_overlap must be a non-negative integer")
                    continue
            except (ValueError, TypeError):
                errors.append("chunk_overlap must be an integer")
                continue

        if key == "top_k":
            try:
                val = int(value)
                if val < 1:
                    errors.append("top_k must be a positive integer")
                    continue
            except (ValueError, TypeError):
                errors.append("top_k must be an integer")
                continue

        if key == "max_iterations":
            try:
                val = int(value)
                if val < 1:
                    errors.append("max_iterations must be a positive integer")
                    continue
            except (ValueError, TypeError):
                errors.append("max_iterations must be an integer")
                continue

        # Apply the update
        config.set(key, value)
        updated_keys.append(key)

    if errors:
        return jsonify({"status": "error", "message": "; ".join(errors), "updated": updated_keys}), 400

    return jsonify({"status": "ok", "updated": updated_keys})


@bp.route("/api/config/test-connection", methods=["POST"])
def test_connection():
    """
    Test LLM backend connectivity and return status.

    Optionally accepts JSON: {"backend": str, "api_key": str, "model": str}
    to test a specific backend. If no body is provided, tests the currently
    configured backend.

    Returns JSON: {"status": "connected"|"error", "backend": str, "model": str, "message": str}
    """
    from config import config

    data = request.get_json() or {}

    # Use provided values or fall back to current config
    backend_name = data.get("backend", config.get("llm_backend", "ollama"))
    model_name = data.get("model", config.get("llm_model", "Llama-3.2-3B-Instruct-Q4_K_M"))

    # Determine API key
    if "api_key" in data:
        api_key = data["api_key"]
    elif backend_name == "openai":
        api_key = config.get("api_key_openai")
    elif backend_name == "gemini":
        api_key = config.get("api_key_gemini")
    else:
        api_key = None

    base_url = data.get("base_url", config.get("ollama_base_url", "http://localhost:11434"))

    # Map backend string to enum
    backend_map = {"ollama": LLMBackend.OLLAMA, "openai": LLMBackend.OPENAI, "gemini": LLMBackend.GEMINI}
    backend_enum = backend_map.get(backend_name)
    if backend_enum is None:
        return jsonify({
            "status": "error",
            "backend": backend_name,
            "model": model_name,
            "message": f"Unknown backend '{backend_name}'. Must be one of: ollama, openai, gemini",
        }), 400

    try:
        llm_config = LLMConfig(
            backend=backend_enum,
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
        )
        client = LLMClient(llm_config)
        result = client.test_connection()
        return jsonify(result)
    except LLMClientError as e:
        return jsonify({
            "status": "error",
            "backend": backend_name,
            "model": model_name,
            "message": e.reason,
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "backend": backend_name,
            "model": model_name,
            "message": str(e),
        })
