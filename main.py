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

    def __init__(self, max_messages: int = 50, max_tokens: int = 30):
        """
        Initialize conversation memory.

        Args:
            max_messages: Maximum number of messages to retain.
        """
        self._history: list = []
        self.max_messages = max_messages
        self.max_tokens = max_tokens

    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to history. Drops oldest if over max_messages.

        Args:
            role: Message role ("user" or "assistant").
            content: Message text content.
        """
        self._history.append({"role": role, "content": content})
        
        # print(self._history)

        # Simple trimming: drop oldest messages when limit exceeded
        #while len(self._history) > self.max_messages:
           # self._history.pop(0)
        
        #while self._estimate_tokens(content) > self.max_tokens:
        #    self._history.pop(0)

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
    
    def _estimate_tokens(self, text: str ="") -> int:
        """Estimate token count for a text string.
    
        Hint: A common approximation for English text is that
        1 token ≈ 4 characters (or ~0.75 words). You can also
        use a proper tokenizer like tiktoken for exact counts.

        Args:
            text: The text to estimate tokens for.

        Returns:
            Estimated number of tokens.
        """
        
        history_char = 0
        
        for message in self._history:
          history_char += len(message["content"])
        
        amount_characters = len(text) + history_char
        CHARACTER_PER_TOKEN = 4
        
        tokens = amount_characters / CHARACTER_PER_TOKEN
        
        return tokens

    def needs_summarizations(self, keep_recent: int = 6) -> bool:
        tokens = self._estimate_tokens()
        return tokens > self.max_tokens and len(self._history) > keep_recent
    
    def summarize_old_messages(self, llm_client) -> str:
        arr = self._history.copy()
        
        # The recent comments comes first
        arr.reverse()
        
        recent_messages: list = []
        
        for _ in range(6):
            value = arr.pop(0)
            recent_messages.append(value)
            
        
        old_messages = []
        
        for message in arr:
            string = f"{message["role"]}: {message["content"]}"
            
            old_messages.append(string)
        
        PROMPT = f"Summaraize this messages, preserve key facts. The messages are build on the role then the content. Messages to summarize: {old_messages}"
    
        
        #summary = llm_client.generate(prompt=PROMPT)
        
        summary = "Test summary"
        
        summary_json = {"role": "system", "content": f"[Conversation summary]: {summary}"}
        
        self._history.clear()
        self._history.append(summary_json)
        
        print(self._history)
        
        return summary
        
      
cm = ConversationMemory()

def helper(msg):
    cm.add_message("user", msg)
    if cm.needs_summarizations():
        print("SUMMARIZE OLD MESSAGES")
        cm.summarize_old_messages("llm_client")
    
helper("hejsan denna ska bort")
helper("hejsan")
helper("hejsan")
helper("hejsan")
helper("hejsan")
helper("hejsan")
helper("En")
helper("Två")
helper("Tre")
helper("TreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTreTre")

