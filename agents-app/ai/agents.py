"""Agent definitions for the CrewAI-based agents app.

This module defines the agent configuration dataclass and provides
functions to create CrewAI agents from definitions. Students can
modify agent roles, goals, and backstories to experiment with
different agent behaviors.

Usage:
    from ai.agents import get_agents, create_agent

    definitions = get_agents()
    agents = [create_agent(d) for d in definitions]
"""

from dataclasses import dataclass, field
from typing import Optional

from crewai import Agent


@dataclass
class AgentDefinition:
    """Definition of a CrewAI agent.

    Attributes:
        role: The agent's role title (e.g., "Researcher")
        goal: What the agent aims to achieve
        backstory: Context for the agent's expertise and personality
        tools: List of tool names this agent can use
        allow_delegation: Whether the agent can delegate tasks to others
        verbose: Whether to enable verbose output during execution
    """

    role: str
    goal: str
    backstory: str
    tools: list = field(default_factory=list)
    allow_delegation: bool = False
    verbose: bool = True


def _get_llm_model_string() -> str:
    """
    Build the litellm-compatible model string.

    Newer versions of CrewAI use litellm, which requires a provider prefix
    (e.g., 'ollama/llama3.1' instead of just 'llama3.1'). This function
    reads the app config and constructs the correct model string.
    """
    import os
    from config import config

    backend = config.get("llm_backend", "ollama")
    model = config.get("llm_model", "llama3.1")

    # If model already has a provider prefix, use as-is
    if "/" in model:
        return model

    # Add provider prefix for litellm compatibility
    if backend == "ollama":
        base_url = config.get("ollama_base_url", "http://localhost:11434")
        # Set the base URL so litellm knows where to reach Ollama
        os.environ.setdefault("OLLAMA_API_BASE", base_url)
        return f"ollama/{model}"
    elif backend == "openai":
        return f"openai/{model}"
    elif backend == "gemini":
        return f"gemini/{model}"
    else:
        return model


def create_agent(definition: AgentDefinition, llm_client=None) -> Agent:
    """
    Create a CrewAI Agent from a definition.

    The resulting agent MUST have role, goal, and backstory matching the definition.

    Args:
        definition: AgentDefinition with role, goal, backstory
        llm_client: Optional LLM client override. If not provided, the model
                    string is built from config (with litellm provider prefix).

    Returns:
        CrewAI Agent instance
    """
    llm_model = llm_client or _get_llm_model_string()

    agent = Agent(
        role=definition.role,
        goal=definition.goal,
        backstory=definition.backstory,
        llm=llm_model,
        function_calling_llm=None,  # Force text-based tool calling (ReAct) for local models
        allow_delegation=definition.allow_delegation,
        verbose=definition.verbose,
    )

    return agent


def get_agents() -> list[AgentDefinition]:
    """
    Return the baseline agent definitions for the course.

    The default crew consists of three agents:
    - Researcher: Gathers and analyzes information on a topic
    - Writer: Produces well-structured written content
    - Reviewer: Reviews and improves content quality

    Returns:
        List of AgentDefinition objects for researcher, writer, and reviewer agents.
    """
    researcher = AgentDefinition(
        role="Researcher",
        goal="Gather comprehensive and accurate information on {topic}",
        backstory=(
            "You are an experienced research analyst with a keen eye for detail. "
            "You excel at finding relevant information, identifying key trends, "
            "and synthesizing complex data into clear insights. Your research "
            "forms the foundation for high-quality content creation."
        ),
        tools=[],
        allow_delegation=False,
        verbose=True,
    )

    writer = AgentDefinition(
        role="Writer",
        goal="Write a clear, engaging, and well-structured article about {topic}",
        backstory=(
            "You are a skilled content writer who transforms research findings "
            "into compelling narratives. You have a talent for making complex "
            "topics accessible to a broad audience while maintaining accuracy. "
            "You structure your writing with clear sections and logical flow."
        ),
        tools=[],
        allow_delegation=False,
        verbose=True,
    )

    reviewer = AgentDefinition(
        role="Reviewer",
        goal="Review and improve the written content for clarity, accuracy, and engagement",
        backstory=(
            "You are a meticulous editor and quality reviewer. You check content "
            "for factual accuracy, logical consistency, grammar, and readability. "
            "You provide constructive feedback and suggest improvements that "
            "elevate the overall quality of the final output."
        ),
        tools=[],
        allow_delegation=False,
        verbose=True,
    )

    return [researcher, writer, reviewer]
