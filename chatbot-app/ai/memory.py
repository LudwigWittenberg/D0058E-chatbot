"""
Conversation memory for the Chatbot App.

This module provides a basic ConversationMemory class that stores
messages in a list. Students will extend it with:
- Token-based trimming (Task 1.3 Step 4)
- Sliding window + summarization (Task 1.3 Step 5)

Usage:
    memory = ConversationMemory(max_messages=50)
    memory.add_message("user", "Hello")
    memory.add_message("assistant", "Hi there!")
    history = memory.get_history()
"""


class ConversationMemory:
    """Manages conversation history with a simple fixed-window strategy.

    Messages are stored in a list. When max_messages is exceeded,
    the oldest messages are dropped.
    """

    def __init__(self, max_messages: int = 50):
        """
        Initialize conversation memory.

        Args:
            max_messages: Maximum number of messages to retain.
        """
        self._history: list = []
        self.max_messages = max_messages

    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to history. Drops oldest if over max_messages.

        Args:
            role: Message role ("user" or "assistant").
            content: Message text content.
        """
        self._history.append({"role": role, "content": content})

        # Simple trimming: drop oldest messages when limit exceeded
        while len(self._history) > self.max_messages:
            self._history.pop(0)

    def get_history(self) -> list:
        """Return the full conversation history."""
        return list(self._history)

    def get_recent(self, n: int = 10) -> list:
        """Return the N most recent messages."""
        return list(self._history[-n:])

    def clear(self) -> None:
        """Clear all conversation history."""
        self._history = []

    # TODO (Task 1.3, Step 4): Add token-based trimming
    # - Add max_tokens parameter to __init__
    # - Implement _estimate_tokens(text) method
    # - Modify add_message() to trim by token budget instead of message count

    # TODO (Task 1.3, Step 5): Add summarization
    # - Add needs_summarization() method
    # - Add summarize_old_messages(llm_client) method
    # - Keep recent N messages in full, summarize older ones
