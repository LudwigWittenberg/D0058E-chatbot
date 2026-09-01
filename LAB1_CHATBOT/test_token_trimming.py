"""
Lab 1, Task 1.3, Step 4 — Token Trimming Test Script

This script highlights the DIFFERENCE between message-count trimming
and token-based trimming by sending messages of varying lengths and
showing how token usage grows differently.

Key observation: with token trimming, short messages allow MORE history
to survive, while long messages cause EARLIER trimming — adapting to
actual context usage rather than treating all messages equally.

Usage:
    python test_token_trimming.py

Prerequisites:
    - Chatbot app running on http://localhost:8001
    - Server-side memory with TOKEN-BASED TRIMMING active
      (memory_token_trimming.py copied to chatbot-app/ai/memory.py)
    - Ollama running with num_ctx=4096
    - Python 3.10+ with 'requests' installed
"""

import requests
import sys

BASE_URL = "http://localhost:8001"


def clear_memory():
    """Clear server-side conversation memory."""
    try:
        r = requests.post(f"{BASE_URL}/api/memory/clear")
        r.raise_for_status()
    except requests.ConnectionError:
        print("ERROR: Cannot connect to chatbot app at port 8001.")
        print("Make sure the app is running: python3 chatbot-app/run.py")
        sys.exit(1)


def get_memory():
    """Get current memory state."""
    r = requests.get(f"{BASE_URL}/api/memory")
    return r.json()


def send_message(message):
    """Send a message and return the response + memory stats."""
    r = requests.post(
        f"{BASE_URL}/chat",
        json={"message": message},
        headers={"Content-Type": "application/json"},
    )
    data = r.json()
    return data.get("response", ""), data.get("memory_stats", {})


def print_separator(title):
    print()
    print(f"{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")
    print()


def main():
    print_separator("TOKEN TRIMMING TEST — Lab 1, Task 1.3, Step 4")

    print("This test sends messages of VARYING lengths to show how")
    print("token-based trimming adapts to actual content size.")
    print()

    # =========================================================================
    # PHASE 1: Short messages — should fit many in memory
    # =========================================================================
    print_separator("PHASE 1: Short messages (expect many to fit)")

    clear_memory()
    print("Memory cleared. Sending 15 short messages...\n")

    short_messages = [
        "Hi",
        "My name is Alice",
        "I study at LTU",
        "I like Python",
        "Purple is my color",
        "42 is my number",
        "Yes",
        "Ok",
        "Thanks",
        "Got it",
        "Sure",
        "Right",
        "Cool",
        "Nice",
        "Great",
    ]

    prev_tokens = 0
    print(f"{'Turn':<6} {'Msgs':<6} {'Tokens':<8} {'Added':<8} {'Message sent'}")
    print("-" * 60)

    for i, msg in enumerate(short_messages, 1):
        response, stats = send_message(msg)
        curr_tokens = stats.get("estimated_tokens", 0)
        added = curr_tokens - prev_tokens
        msgs = stats.get("messages_in_memory", 0)
        print(f"{i:<6} {msgs:<6} {curr_tokens:<8} +{added:<7} \"{msg}\"")
        prev_tokens = curr_tokens

    mem = get_memory()
    print(f"\nFinal: {mem['message_count']} messages, ~{mem['estimated_tokens']} tokens")
    print(f"Budget used: {mem['budget_used_pct']}%")

    # Test recall
    print("\n--- Recall test ---")
    response, _ = send_message("What is my name and what do I study?")
    print(f"Bot: {response[:200]}")
    has_alice = "alice" in response.lower()
    has_ltu = "ltu" in response.lower()
    print(f"Remembers Alice: {'✅' if has_alice else '❌'}")
    print(f"Remembers LTU: {'✅' if has_ltu else '❌'}")

    # =========================================================================
    # PHASE 2: Long messages — should fit fewer in memory
    # =========================================================================
    print_separator("PHASE 2: Long messages (expect fewer to fit)")

    clear_memory()
    print("Memory cleared. Sending 10 long messages...\n")

    # Plant a fact first
    send_message("Remember this: my secret code is ALPHA-7749.")

    long_messages = [
        "Explain the complete history of the internet from ARPANET to modern day, including all major milestones.",
        "Describe in detail how a compiler works, covering lexing, parsing, semantic analysis, optimization, and code generation.",
        "Explain the theory of relativity including both special and general relativity with mathematical formulations.",
        "Describe the complete architecture of a modern CPU including pipelining, branch prediction, and cache hierarchy.",
        "Explain how neural networks learn through backpropagation, including the chain rule and gradient descent.",
        "Describe the complete TCP/IP protocol stack with all layers, headers, and handshake mechanisms.",
        "Explain quantum computing including qubits, superposition, entanglement, and quantum gates.",
        "Describe the complete process of DNA replication including enzymes, leading and lagging strands.",
        "Explain the history and evolution of programming languages from assembly to modern functional languages.",
    ]

    prev_tokens = 0
    # Get initial state after the fact-planting message
    mem = get_memory()
    prev_tokens = mem["estimated_tokens"]

    print(f"{'Turn':<6} {'Msgs':<6} {'Tokens':<8} {'Added':<8} {'Message (truncated)'}")
    print("-" * 60)
    print(f"{'0':<6} {mem['message_count']:<6} {prev_tokens:<8} {'—':<8} [planted fact: secret code]")

    for i, msg in enumerate(long_messages, 1):
        response, stats = send_message(msg)
        curr_tokens = stats.get("estimated_tokens", 0)
        added = curr_tokens - prev_tokens
        msgs = stats.get("messages_in_memory", 0)
        # Show if trimming happened (added could be negative if old msgs were removed)
        trimmed = " ⚠️ TRIMMED" if added < 0 or msgs < (i + 1) * 2 else ""
        print(f"{i:<6} {msgs:<6} {curr_tokens:<8} {'+' + str(added) if added >= 0 else str(added):<8} \"{msg[:40]}...\"{trimmed}")
        prev_tokens = curr_tokens

    mem = get_memory()
    print(f"\nFinal: {mem['message_count']} messages, ~{mem['estimated_tokens']} tokens")
    print(f"Budget used: {mem['budget_used_pct']}%")

    # Test recall of the early fact
    print("\n--- Recall test ---")
    response, _ = send_message("What is my secret code?")
    print(f"Bot: {response[:200]}")
    has_code = "alpha-7749" in response.lower() or "alpha" in response.lower()
    print(f"Remembers secret code: {'✅' if has_code else '❌ (trimmed away by long responses)'}")

    # =========================================================================
    # COMPARISON SUMMARY
    # =========================================================================
    print_separator("COMPARISON SUMMARY")

    print("Phase 1 (short messages):")
    print("  - Many messages fit in memory (short = few tokens each)")
    print("  - Early facts likely PRESERVED")
    print()
    print("Phase 2 (long messages):")
    print("  - Fewer messages fit (long responses = many tokens each)")
    print("  - Early facts likely TRIMMED to make room")
    print()
    print("KEY INSIGHT: Token-based trimming adapts to actual content size.")
    print("Message-count trimming would treat 'Hi' and a 500-word explanation")
    print("as equal — token trimming correctly accounts for the difference.")
    print()
    print("Fill in the observation table in your lab report with these numbers.")


if __name__ == "__main__":
    main()
