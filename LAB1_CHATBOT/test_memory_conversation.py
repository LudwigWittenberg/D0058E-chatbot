"""
Lab 1, Task 1.3 — Context Memory Test Script (Cross-Platform Python Version)

This script works on Windows, macOS, and Linux — no bash required.
It sends a series of messages to the chatbot (which manages history
server-side), plants specific facts, then tests recall.

Usage:
    python test_memory_conversation.py

Prerequisites:
    - Chatbot app running on http://localhost:8001 with server-side memory
      (Task 1.3 Step 1 completed — routes.py replaced)
    - LLM server running on port 11434
    - Python 3.10+ with 'requests' installed (pip install requests)
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8001"
LLM_SERVER = "http://localhost:11434"


def get_context_budget():
    """Query the LLM server for its configured context window size."""
    try:
        r = requests.get(f"{LLM_SERVER}/api/ps")
        if r.status_code == 200:
            data = r.json()
            models = data.get("models", [])
            if models:
                return models[0].get("context_length", 4096)
    except Exception:
        pass
    return 4096  # default fallback


CONTEXT_BUDGET = get_context_budget()


def clear_memory():
    """Clear the server-side conversation memory."""
    try:
        r = requests.post(f"{BASE_URL}/api/memory/clear")
        r.raise_for_status()
        print("  Memory cleared.\n")
    except requests.ConnectionError:
        print("ERROR: Cannot connect to chatbot app. Is it running on port 8001?")
        sys.exit(1)


def get_memory_stats():
    """Fetch and display current memory state."""
    r = requests.get(f"{BASE_URL}/api/memory")
    data = r.json()
    msg_count = data["message_count"]
    tokens = data["estimated_tokens"]
    pct = data["budget_used_pct"]
    return msg_count, tokens, pct


def send_message(message, show_response=False):
    """
    Send a message to the chatbot.
    Returns the assistant's response text.
    """
    r = requests.post(
        f"{BASE_URL}/chat",
        json={"message": message},
        headers={"Content-Type": "application/json"},
    )
    data = r.json()
    response_text = data.get("response", "[no response]")

    # Check if the response is an error (context window exceeded, etc.)
    is_error = response_text.startswith("Error:")
    if is_error:
        print(f"  ⚠️  CONTEXT OVERFLOW: {response_text[:150]}")

    if show_response and not is_error:
        # Show first 200 chars of the bot's response
        preview = response_text[:200] + ("..." if len(response_text) > 200 else "")
        print(f"  Bot says: {preview}")

    # Show memory stats (may be in the response or fetched separately)
    stats = data.get("memory_stats")
    if stats:
        msg_count = stats["messages_in_memory"]
        max_msgs = stats.get("max_messages", "?")
        tokens = stats["estimated_tokens"]
        pct = stats["budget_used_pct"]
    else:
        msg_count, tokens, pct = get_memory_stats()
        max_msgs = "?"
    print(f"  Memory: {msg_count} msgs (max {max_msgs}) | ~{tokens} tokens | {pct}% of {CONTEXT_BUDGET} budget")

    return response_text


def main():
    print("=" * 60)
    print("  Context Memory Test — Lab 1, Task 1.3")
    print("=" * 60)
    print()
    print("Prerequisites:")
    print("  - Server-side memory wired up (Step 1 complete)")
    print(f"  - Context window: {CONTEXT_BUDGET} tokens (queried from server)")
    print("  - Chatbot running at http://localhost:8001")
    print()

    # --- Clear memory ---
    print("Clearing server memory...")
    clear_memory()

    # Query max_messages setting
    try:
        r = requests.get(f"{BASE_URL}/api/memory")
        max_msgs = r.json().get("max_messages", "?")
        print(f"  max_messages in memory: {max_msgs}")
        print()
    except Exception:
        max_msgs = "?"

    # --- Phase 1: Plant specific facts ---
    print("-" * 60)
    print("Phase 1: Planting facts (messages 1-5)")
    print("-" * 60)
    print()

    facts = [
        ("name", "My name is Alice and I'm a computer science student at LTU."),
        ("color", "My favorite color is purple and my lucky number is 42."),
        ("project", "I'm working on a project about autonomous drones for forest monitoring."),
        ("pet", "I have a cat named Pixel who likes to sit on my keyboard."),
        ("deadline", "My thesis deadline is March 15th and my supervisor is Professor Lindström."),
    ]

    for i, (label, message) in enumerate(facts, 1):
        print(f"[Message {i}] Planting fact: {label}")
        print(f"  >>> {message}")
        send_message(message)
        print()

    # --- Phase 2: Fill context with unrelated messages ---
    print("-" * 60)
    print("Phase 2: Filling context with unrelated messages (6-10)")
    print("-" * 60)
    print()

    filler_messages = [
        "Can you explain how binary search works?",
        "What is the difference between a stack and a queue?",
        "How does garbage collection work in Python?",
        "Explain the concept of Big O notation with examples.",
        "What are the SOLID principles in software engineering?"
    ]

    for i, message in enumerate(filler_messages):
        msg_num = i + 6
        print(f"[Message {msg_num}] {message[:50]}...")
        send_message(message)
        print()

    # --- Phase 3: Test recall ---
    print("-" * 60)
    print("Phase 3: Testing recall of early facts (messages 11-15)")
    print("-" * 60)
    print()

    recall_tests = [
        ("What is my name and where do I study?", "Alice, LTU"),
        ("What is my favorite color and lucky number?", "purple, 42"),
        ("What is my project about?", "autonomous drones, forest monitoring"),
        ("What is my cat's name?", "Pixel"),
        ("When is my thesis deadline and who is my supervisor?", "March 15th, Professor Lindström"),
    ]

    results = []
    for i, (question, expected) in enumerate(recall_tests, 1):
        print(f"[RECALL TEST {i}] {question}")
        print(f"  >>> {question}")
        response = send_message(question, show_response=True)
        print(f"  Expected: {expected}")

        # Simple check: are the key words in the response?
        keywords = [w.strip().lower() for w in expected.split(",")]
        found = [kw for kw in keywords if kw in response.lower()]
        missed = [kw for kw in keywords if kw not in response.lower()]

        if missed:
            print(f"  ❌ FORGOTTEN: {', '.join(missed)}")
            results.append(("FAIL", question, missed))
        else:
            print(f"  ✅ Remembered: {', '.join(found)}")
            results.append(("PASS", question, found))
        print()

    # --- Summary ---
    print("=" * 60)
    print("  RESULTS SUMMARY")
    print("=" * 60)
    print()

    msg_count, tokens, pct = get_memory_stats()
    print(f"Final memory state: {msg_count} msgs | ~{tokens} tokens | {pct}% budget used")
    print()

    passed = sum(1 for r in results if r[0] == "PASS")
    failed = sum(1 for r in results if r[0] == "FAIL")
    print(f"Recall tests: {passed} passed, {failed} failed out of {len(results)}")
    print()

    if failed > 0:
        print("Forgotten facts:")
        for status, question, items in results:
            if status == "FAIL":
                print(f"  - {question} → missed: {', '.join(items)}")
        print()
        print("This means the context window was too small to hold all messages,")
        print("or max_messages trimmed the early facts from memory.")
    else:
        print("All facts remembered! The context window is large enough for this test.")
        print("Try reducing max_messages to 10 in routes.py and re-run to see forgetting.")

    print()
    print("Next steps:")
    print("  1. Change _memory = ConversationMemory(max_messages=10) in routes.py")
    print("  2. Re-run this script to see forgetting happen sooner")
    print("  3. Implement token-based trimming (Step 4)")
    print("  4. Implement sliding window + summary (Step 5)")


if __name__ == "__main__":
    main()
