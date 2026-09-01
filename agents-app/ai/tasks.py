"""Task definitions for the CrewAI-based agents app.

This module defines the task configuration dataclass and provides
functions to create CrewAI tasks from definitions. Students can
modify task descriptions and expected outputs to experiment with
different crew workflows.

Usage:
    from ai.tasks import get_tasks, create_task

    definitions = get_tasks()
    tasks = [create_task(d, agent) for d, agent in zip(definitions, agents)]
"""

from dataclasses import dataclass, field
from typing import Optional

from crewai import Task


@dataclass
class TaskDefinition:
    """Definition of a CrewAI task.

    Attributes:
        description: What the task requires the agent to do
        expected_output: Description of the expected result format
        agent_role: Role of the agent assigned to this task (used for matching)
        context_tasks: List of task descriptions that provide context to this task
    """

    description: str
    expected_output: str
    agent_role: str  # Role of the agent assigned to this task
    context_tasks: list = field(default_factory=list)


def create_task(definition: TaskDefinition, agent) -> Task:
    """
    Create a CrewAI Task from a definition.

    The resulting task MUST have description and expected_output matching the definition.

    Args:
        definition: TaskDefinition with description and expected output
        agent: The CrewAI Agent assigned to this task

    Returns:
        CrewAI Task instance
    """
    task = Task(
        description=definition.description,
        expected_output=definition.expected_output,
        agent=agent,
    )

    return task


def get_tasks() -> list[TaskDefinition]:
    """
    Return the baseline task definitions for the course.

    The default pipeline consists of three sequential tasks:
    1. Research: Gather information on the topic
    2. Write: Create content based on research
    3. Review: Polish and improve the written content

    Returns:
        List of TaskDefinition objects for the default crew pipeline.
    """
    research_task = TaskDefinition(
        description=(
            "Research the topic: {topic}. "
            "1. Identify the key concepts, trends, and important details. "
            "2. Find relevant facts, statistics, and expert opinions. "
            "3. Organize your findings into a structured research brief. "
            "4. Note any areas that need further investigation."
        ),
        expected_output=(
            "A comprehensive research brief with key findings, "
            "relevant facts and statistics, identified trends, "
            "and organized source material ready for content creation."
        ),
        agent_role="Researcher",
    )

    writing_task = TaskDefinition(
        description=(
            "Using the research provided, write a well-structured article about {topic}. "
            "1. Create an engaging introduction that hooks the reader. "
            "2. Organize the body into clear sections with logical flow. "
            "3. Include relevant facts and examples from the research. "
            "4. Write a conclusion that summarizes key points and provides a call to action."
        ),
        expected_output=(
            "A well-written article in markdown format with clear sections, "
            "engaging introduction, informative body paragraphs, "
            "and a strong conclusion. Each section should have 2-3 paragraphs."
        ),
        agent_role="Writer",
    )

    review_task = TaskDefinition(
        description=(
            "Review the written article about {topic}. "
            "1. Check for factual accuracy and logical consistency. "
            "2. Improve clarity, grammar, and readability. "
            "3. Ensure the article flows well and engages the reader. "
            "4. Provide the final polished version ready for publication."
        ),
        expected_output=(
            "A polished, publication-ready article in markdown format "
            "with improved clarity, corrected errors, and enhanced "
            "readability. Include a brief review summary noting changes made."
        ),
        agent_role="Reviewer",
    )

    return [research_task, writing_task, review_task]
