"""Crew assembly and execution for the agents app.

This module provides functions to assemble a CrewAI Crew from agents
and tasks, and to execute the crew with given inputs. Students can
experiment with different process types and configurations.

Usage:
    from ai.crew import run_crew_pipeline

    result = run_crew_pipeline(topic="AI in healthcare")

    # Or with progress logging:
    result = run_crew_pipeline(
        topic="AI in healthcare",
        on_progress=lambda msg: print(msg),
    )
"""

from typing import Callable, Optional

from crewai import Crew, Process

from ai.agents import get_agents, create_agent, AgentDefinition
from ai.tasks import get_tasks, create_task, TaskDefinition


def assemble_crew(
    agents: list,
    tasks: list,
    process_type: str = "sequential",
    verbose: bool = True,
    on_task_done: Optional[Callable] = None,
) -> Crew:
    """
    Assemble a CrewAI Crew from agents and tasks.

    Args:
        agents: List of CrewAI Agent instances
        tasks: List of CrewAI Task instances
        process_type: "sequential" or "hierarchical"
        verbose: Whether to enable verbose output
        on_task_done: Optional callback fired when a task completes

    Returns:
        Configured Crew instance ready for kickoff
    """
    if process_type == "hierarchical":
        process = Process.hierarchical
    else:
        process = Process.sequential

    kwargs = dict(
        agents=agents,
        tasks=tasks,
        process=process,
        verbose=verbose,
    )
    if on_task_done:
        kwargs["task_callback"] = on_task_done

    crew = Crew(**kwargs)
    return crew


def execute_crew(crew: Crew, inputs: dict = None) -> dict:
    """
    Execute a crew and return results.

    Args:
        crew: Assembled Crew instance
        inputs: Optional input variables for tasks (e.g., {"topic": "AI"})

    Returns:
        {"result": str, "tasks_output": list[dict], "token_usage": dict}
    """
    if inputs is None:
        inputs = {}

    try:
        crew_output = crew.kickoff(inputs=inputs)

        # Extract results from CrewOutput
        result_text = str(crew_output)

        # Extract individual task outputs if available
        tasks_output = []
        if hasattr(crew_output, "tasks_output") and crew_output.tasks_output:
            for task_output in crew_output.tasks_output:
                tasks_output.append({
                    "description": getattr(task_output, "description", ""),
                    "output": str(task_output),
                    "agent": getattr(task_output, "agent", ""),
                })

        # Extract token usage if available
        token_usage = {}
        if hasattr(crew_output, "token_usage") and crew_output.token_usage:
            token_usage = dict(crew_output.token_usage)

        return {
            "result": result_text,
            "tasks_output": tasks_output,
            "token_usage": token_usage,
        }

    except Exception as e:
        return {
            "result": f"Crew execution failed: {str(e)}",
            "tasks_output": [],
            "token_usage": {},
        }


def on_task_done_callback(task_output) -> None:
    """
    Callback invoked when a task completes.

    CrewAI calls this function after an agent produces its final answer
    for a task. The task_output contains the result string that will be
    passed as context to the next task in the pipeline.

    Args:
        task_output: CrewAI TaskOutput object with attributes:
            - agent: name of the agent that completed the task
            - raw: the raw output string (passed to next agent as context)
            - description: the task description that was executed
    """
    agent_name = getattr(task_output, "agent", "unknown")
    print(f"[TASK_DONE:{agent_name}] Task completed")


def build_agent_map(
    agent_defs: list[AgentDefinition],
    agents: list,
) -> dict:
    """
    Build a mapping from agent role names to CrewAI Agent instances.

    This is used to match tasks to their assigned agents by role.

    Args:
        agent_defs: List of AgentDefinition objects (with .role field).
        agents: List of CrewAI Agent instances (same order as agent_defs).

    Returns:
        Dictionary mapping role name (str) to CrewAI Agent instance.
    """
    agent_map = {}
    for a_def, agent in zip(agent_defs, agents):
        agent_map[a_def.role] = agent
    return agent_map


def initialize_crew(
    process_type: Optional[str] = None,
    on_progress: Optional[Callable[[str], None]] = None,
) -> Crew:
    """
    Initialize the crew pipeline (steps 1-5): load agents, load tasks,
    match them, and assemble the Crew instance.

    This does NOT execute the crew — call run_crew() separately.

    Args:
        process_type: "sequential" or "hierarchical". If None, reads from config.
        on_progress: Optional callback for progress messages.

    Returns:
        Assembled Crew instance ready for execution.

    Raises:
        NotImplementedError: If required ai/ modules are not yet implemented.
    """
    def _log(message: str):
        if on_progress:
            on_progress(message)

    from config import config

    # Resolve process type
    if process_type is None:
        process_type = config.get("crew_process_type", "sequential")

    # 1. Load agent definitions
    _log("Loading agent definitions...")
    agent_defs = get_agents()
    if not agent_defs:
        raise NotImplementedError("Agent definitions not yet implemented")

    # Check if agents are still placeholders
    for a_def in agent_defs:
        if "TODO:" in a_def.goal or "TODO:" in a_def.backstory:
            raise ValueError(
                f"Agent '{a_def.role}' still contains placeholder text (TODO:). "
                "Replace the placeholder definitions in ai/agents.py with your own."
            )

    # 2. Create agent instances
    _log("Creating agent instances...")
    agents = []
    for agent_def in agent_defs:
        agent = create_agent(agent_def)
        if agent is None:
            raise NotImplementedError("create_agent not yet implemented")
        agents.append(agent)
        _log(f"  Agent created: {agent_def.role}")

    # 3. Load task definitions
    _log("Loading task definitions...")
    task_defs = get_tasks()
    if not task_defs:
        raise NotImplementedError("Task definitions not yet implemented")

    # Check if tasks are still placeholders
    for t_def in task_defs:
        if "TODO:" in t_def.description or "TODO:" in t_def.expected_output:
            raise ValueError(
                f"Task for agent '{t_def.agent_role}' still contains placeholder text (TODO:). "
                "Replace the placeholder definitions in ai/tasks.py with your own."
            )

    # 4. Create task instances (match tasks to agents by role)
    _log("Creating task instances...")
    agent_map = build_agent_map(agent_defs, agents)
    tasks = []
    for task_def in task_defs:
        assigned_agent = agent_map.get(task_def.agent_role)
        if assigned_agent is None:
            _log(f"  Warning: No agent found for role '{task_def.agent_role}'")
            continue
        task = create_task(task_def, assigned_agent)
        if task is None:
            raise NotImplementedError("create_task not yet implemented")
        tasks.append(task)
        _log(f"  Task created: {task_def.description[:60]}...")

    # 5. Assemble crew (callbacks will be set at execution time via run_crew)
    _log("Assembling crew...")

    crew = assemble_crew(
        agents=agents,
        tasks=tasks,
        process_type=process_type,
        verbose=True,
    )
    if crew is None:
        raise NotImplementedError("assemble_crew not yet implemented")
    _log(f"Crew assembled with process type: {process_type}")
    _log("Crew initialization complete. Ready to execute.")

    return crew


def run_crew(
    crew: Crew,
    topic: str,
    on_progress: Optional[Callable[[str], None]] = None,
) -> dict:
    """
    Execute an initialized crew on a given topic (step 6).

    Args:
        crew: An assembled Crew instance (from initialize_crew).
        topic: The topic/input for the crew tasks.
        on_progress: Optional callback for progress messages.

    Returns:
        {"result": str, "tasks_output": list[dict], "token_usage": dict}
    """
    def _log(message: str):
        if on_progress:
            on_progress(message)

    # Set callbacks directly on the Crew's Pydantic fields
    import datetime

    def _task_done_cb(task_output):
        agent_name = getattr(task_output, "agent", "unknown")
        ts = datetime.datetime.now().isoformat()
        with open("/tmp/crewai_callbacks.log", "a") as f:
            f.write(f"[{ts}] TASK_DONE_CB agent={agent_name}\n")
        _log(f"[TASK_DONE:{agent_name}] Task completed")
        on_task_done_callback(task_output)

        # Feed completed task output to WordCountTool for the next agent
        try:
            from ai.tools import WordCountTool
            raw_output = getattr(task_output, "raw", "") or ""
            if raw_output:
                WordCountTool._article_text = raw_output

                # Auto-execute tool after Writer completes — inject stats into
                # Reviewer's context so the 3B model reliably reports them
                if "Writer" in agent_name:
                    wc_tool = WordCountTool()
                    tool_result = wc_tool._run(text="count")
                    _log(f"[AUTO_TOOL:word_counter] Writer done → auto-executed: {tool_result}")

                    # Save tool execution to a response file (visible in UI "Load Responses")
                    import datetime as _dt
                    _ts = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
                    _tool_filename = f"/tmp/crew_response_{_llm_call_count[0] + 1:03d}_TOOL_word_counter_{_ts}.txt"
                    _llm_call_count[0] += 1
                    try:
                        with open(_tool_filename, "w", encoding="utf-8") as _tf:
                            _tf.write("*** TOOL EXECUTION: word_counter ***\n")
                            _tf.write(f"Triggered by: Writer task completion\n")
                            _tf.write(f"Input: article text ({len(WordCountTool._article_text)} characters)\n")
                            _tf.write(f"Timestamp: {_ts}\n")
                            _tf.write(f"\n{'='*60}\n")
                            _tf.write(f"TOOL OUTPUT:\n")
                            _tf.write(f"{'='*60}\n\n")
                            _tf.write(f"{tool_result}\n")
                    except Exception:
                        pass

                    # Patch the Reviewer's task description to include the stats
                    for task in new_crew.tasks:
                        if hasattr(task, 'agent') and task.agent and task.agent.role == "Reviewer":
                            task.description = task.description + (
                                f"\n\n--- TOOL RESULT (word_counter) ---\n"
                                f"The word_counter tool has been executed on the article. Results:\n"
                                f"{tool_result}\n"
                                f"Include these statistics in your review."
                            )
                            break
        except (ImportError, AttributeError):
            pass

    # Re-create crew with task_callback only
    from crewai import Crew as CrewClass
    new_crew = CrewClass(
        agents=crew.agents,
        tasks=crew.tasks,
        process=crew.process,
        verbose=crew.verbose,
        task_callback=_task_done_cb,
    )

    _log(f"Starting crew execution with topic: {topic}")

    # Set up tool logging so tool invocations appear in the execution log
    try:
        from ai.tools import set_tool_logger
        set_tool_logger(_log)
    except ImportError:
        pass

    # Disable native tool calling by patching the OpenAI client's create method
    # Note: With local Ollama models, tool execution may not trigger reliably
    # The model may produce tool-call-like output without CrewAI executing the Python code
    from openai.resources.chat.completions.completions import Completions
    _original_completions_create = Completions.create

    def _patched_completions_create(self, *args, **kwargs):
        # Log the call (keep tools in request — Ollama handles them natively)
        _llm_call_count[0] += 1
        n = _llm_call_count[0]
        messages = kwargs.get("messages", [])
        model = kwargs.get("model", "?")

        # Detect agent from system message
        for msg in messages:
            if msg.get("role") == "system":
                content = msg.get("content", "")
                import re
                role_match = re.search(r"Role:\s*(.+?)[\n]", content)
                if role_match:
                    _current_agent_name[0] = role_match.group(1).strip()
                elif "You are" in content:
                    start = content.find("You are") + 8
                    end = content.find(".", start)
                    if end > start:
                        _current_agent_name[0] = content[start:end].strip()[:30]
                break

        agent = _current_agent_name[0] or "unknown"

        # Log prompt (last user message)
        last_user = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user = msg.get("content", "")
                break

        _log(f"[Communication round #{n} for Agent: {agent}]")
        _log(f"[LLM_CALL #{n}] Prompt ({len(messages)} messages, model={model}): {last_user}")

        # Call original (without tools)
        response = _original_completions_create(self, *args, **kwargs)

        # Log response
        try:
            resp_text = response.choices[0].message.content or ""
            _log(f"[LLM_RESPONSE #{n}] ({len(resp_text)} chars): {resp_text}")

            # Save full response to file
            import datetime
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = agent.replace(" ", "_").replace("/", "_")[:20]
            filename = f"/tmp/crew_response_{n:03d}_{safe_name}_{ts}.txt"
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(f"Agent: {agent}\n")
                    f.write(f"LLM Call: #{n}\n")
                    f.write(f"Model: {model}\n")
                    f.write(f"Messages: {len(messages)}\n")
                    f.write(f"\n{'='*60}\n")
                    f.write(f"FULL PROMPT ({len(messages)} messages):\n")
                    f.write(f"{'='*60}\n\n")
                    for msg in messages:
                        role = msg.get("role", "?")
                        content = msg.get("content", "")
                        f.write(f"--- [{role}] ---\n")
                        f.write(str(content) + "\n\n")
                    f.write(f"\n{'='*60}\n")
                    f.write(f"FULL RESPONSE:\n")
                    f.write(f"{'='*60}\n\n")
                    f.write(resp_text)
            except Exception:
                pass
        except Exception:
            pass

        return response

    Completions.create = _patched_completions_create

    # Also track current agent name
    _llm_call_count = [0]
    _current_agent_name = [None]

    # Wrap tool._run to ensure logging appears in execution logs
    for agent_obj in new_crew.agents:
        if hasattr(agent_obj, 'tools') and agent_obj.tools:
            for tool in agent_obj.tools:
                original_run = tool._run
                tool_name = tool.name

                def make_wrapped(orig, name):
                    def wrapped_run(*args, **kwargs):
                        _log(f"[TOOL_CALL:{name}] Input: {str(args[0]) if args else 'none'}")
                        result = orig(*args, **kwargs)
                        _log(f"[TOOL_RESULT:{name}] {result}")
                        return result
                    return wrapped_run

                # Use object.__setattr__ for Pydantic models
                object.__setattr__(tool, '_run', make_wrapped(original_run, tool_name))

    # Execute the crew
    result = execute_crew(new_crew, inputs={"topic": topic})

    # Restore
    Completions.create = _original_completions_create
    try:
        from ai.tools import set_tool_logger
        set_tool_logger(None)
    except ImportError:
        pass

    if result is None:
        raise NotImplementedError("execute_crew not yet implemented")

    _log("Crew execution completed successfully.")
    return result


def run_crew_pipeline(
    topic: str,
    process_type: Optional[str] = None,
    on_progress: Optional[Callable[[str], None]] = None,
) -> dict:
    """
    Full crew pipeline: initialize + execute in one call.

    Convenience function that calls initialize_crew() then run_crew().
    Use this when you don't need separate control over init vs execution.

    Args:
        topic: The topic/input for the crew tasks.
        process_type: "sequential" or "hierarchical". If None, reads from config.
        on_progress: Optional callback for progress messages.

    Returns:
        {"result": str, "tasks_output": list[dict], "token_usage": dict}
    """
    crew = initialize_crew(process_type=process_type, on_progress=on_progress)
    return run_crew(crew, topic, on_progress=on_progress)
