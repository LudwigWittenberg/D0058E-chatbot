"""
Prompt templates for the Chatbot App.

This module defines system messages and response formatting
templates used by the chat logic.
"""

# Persona definitions mapping persona names to system prompts
PERSONAS = {
    "default": (
        "You are a helpful assistant. You provide clear, accurate, and concise "
        "answers to user questions. If you don't know something, say so honestly."
    ),
    "helpful": (
        "You are an extremely helpful and patient assistant. You go above and "
        "beyond to help users understand topics, providing examples and "
        "step-by-step explanations when useful. Always be encouraging."
    ),
    "creative": (
        "You are a creative and imaginative assistant. You think outside the box, "
        "offer novel perspectives, and use vivid language. You enjoy brainstorming "
        "and exploring unconventional ideas."
    ),
    "concise": (
        "You are a concise assistant. You give brief, direct answers without "
        "unnecessary elaboration. Bullet points over paragraphs. No filler words."
    ),
    "soviet": (
        "You are a beurocratic soviet assistant. You give dry, not precise answers "
        "answer socialistic propaganda. cite Lenin, Marx and Stalin."
    ),
}



def list_personas() -> list[str]:
    """Return all available persona names."""
    return list(PERSONAS.keys())


def build_chat_prompt(
    user_message: str,
    system_prompt: str,
    context: str = ""
) -> str:
    """
    Construct a complete prompt from components.

    Combines the system prompt, optional context (e.g., from RAG retrieval),
    and the user message into a single formatted prompt string.

    Args:
        user_message: The user's message.
        system_prompt: System instructions.
        context: Optional RAG context to include.

    Returns:
        Formatted prompt string containing all components.
    """
    parts = []

    # System instructions
    parts.append(f"[System]\n{system_prompt}")

    # Optional context (e.g., from RAG retrieval)
    if context:
        parts.append(f"[Context]\n{context}")

    # User message
    parts.append(f"[User]\n{user_message}")

    return "\n\n".join(parts)


def get_system_prompt(persona: str = "default") -> str:
    """
    Get a system prompt by persona name.

    Supported personas: "default", "helpful", "creative", "concise".
    Falls back to "default" if the persona name is not recognized.

    Args:
        persona: Name of the persona template.

    Returns:
        System prompt string.
    """
    return PERSONAS.get(persona, PERSONAS["default"])
