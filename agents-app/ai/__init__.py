"""Agents application AI module.

This module contains the AI logic for the multi-agent orchestration app.
Students modify files in this folder to experiment with:
- Agent definitions (roles, goals, backstories)
- Task configurations (descriptions, expected outputs)
- Crew assembly (process types, agent-task assignments)
- Tool integrations (added in Task 3.5)

Key modules:
    agents.py - Agent definitions and creation
    tasks.py  - Task definitions and creation
    crew.py   - Crew assembly and execution
    tools.py  - Custom tools (initially empty, students implement)
"""

from ai.agents import AgentDefinition, create_agent, get_agents
from ai.tasks import TaskDefinition, create_task, get_tasks
from ai.crew import assemble_crew, execute_crew, run_crew_pipeline, initialize_crew, run_crew

__all__ = [
    "AgentDefinition",
    "create_agent",
    "get_agents",
    "TaskDefinition",
    "create_task",
    "get_tasks",
    "assemble_crew",
    "execute_crew",
    "run_crew_pipeline",
    "initialize_crew",
    "run_crew",
]
