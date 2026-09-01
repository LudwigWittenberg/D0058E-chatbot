"""
Lab 1, Task 1.3, Step 5 — Memory Summarization Test Script

This script uses the SAME conversation as test_memory_conversation.py
so you can directly compare results across all three strategies:
  - test_memory_conversation.py  → max_messages trimming
  - test_token_trimming.py       → token-based trimming
  - test_memory_summarization.py → sliding window + summary (this script)

It displays token usage per turn so you can fill in the observation table
and see the effect of summarization (token count drops when summary replaces
old messages, then grows again).

Usage:
    python test_memory_summarization.py

Prerequisites:
    - Chatbot app running on http://localhost:8001
    - memory_with_summary.py active as chatbot-app/ai/memory.py
    - routes_with_summary.py active as chatbot-app/web/routes.py
    - LLM server running with n_ctx=2048
    - Python 3.10+ with 'requests' installed
"""

import requests
import json
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
    """Get full memory state."""
    r = requests.get(f"{BASE_URL}/api/memory")
    return r.json()


def send_message(message):
    """Send a message and return response text + memory stats."""
    r = requests.post(
        f"{BASE_URL}/chat",
        json={"message": message},
        headers={"Content-Type": "application/json"},
    )
    data = r.json()
    return data.get("response", ""), data.get("memory_stats", {})


def print_separator(title):
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
    print()


def main():
    print_separator("MEMORY SUMMARIZATION TEST — Lab 1, Task 1.3, Step 5")

    print("Uses the SAME conversation as test_memory_conversation.py")
    print("so you can compare results directly.\n")
    print("Watch for:")
    print("  📋 = summarization triggered (token count drops)")
    print("  The token count should DROP when old messages are replaced by a summary,")
    print("  then GROW again as new messages accumulate.\n")

    # =========================================================================
    # Setup
    # =========================================================================
    clear_memory()
    print("Memory cleared.\n")

    # =========================================================================
    # SAME conversation as test_memory_conversation.py
    # =========================================================================

    # Phase 1: Plant facts (same as test_memory_conversation.py)
    facts = [
        ("name", "My name is Alice and I'm a computer science student at LTU."),
        ("color", "My favorite color is purple and my lucky number is 42."),
        ("project", "I'm working on a project about autonomous drones for forest monitoring."),
        ("pet", "I have a cat named Pixel who likes to sit on my keyboard."),
        ("deadline", "My thesis deadline is March 15th and my supervisor is Professor Lindström."),
    ]

    # Phase 2: Filler messages (same as test_memory_conversation.py)
    filler_messages = [
        "Can you explain how binary search works?",
        "What is the difference between a stack and a queue?",
        "How does garbage collection work in Python?",
        "Explain the concept of Big O notation with examples.",
        "What are the SOLID principles in software engineering?",
    ]

    # Phase 3: Recall questions (same as test_memory_conversation.py)
    recall_tests = [
        ("What is my name and where do I study?", "alice"),
        ("What is my favorite color and lucky number?", "purple"),
        ("What is my project about?", "drone"),
        ("What is my cat's name?", "pixel"),
        ("When is my thesis deadline and who is my supervisor?", "march"),
    ]

    # =========================================================================
    # Run conversation and track token usage per turn
    # =========================================================================

    print(f"{'Turn':<6} {'Msgs':<6} {'Tokens':<8} {'Δ Tokens':<10} {'Sum.Cost':<10} {'Event':<15} {'Message sent'}")
    print("-" * 100)

    prev_tokens = 0
    turn = 0
    total_summary_tokens = 0  # Track cumulative summarization cost

    # --- Phase 1: Facts ---
    for label, message in facts:
        turn += 1
        response, stats = send_message(message)
        msgs = stats.get("messages_in_memory", 0)
        tokens = stats.get("estimated_tokens", 0)
        delta = tokens - prev_tokens
        summarized = stats.get("summarized_this_turn", False)
        sum_cost = stats.get("summary_tokens_used", 0)
        total_summary_tokens += sum_cost
        event = "📋 SUMMARIZED" if summarized else ""
        compressed = stats.get("response_compressed", False)
        if compressed:
            orig_tok = stats.get("response_original_tokens", 0)
            stored_tok = stats.get("response_stored_tokens", 0)
            event = f"🗜️ compressed {orig_tok}→{stored_tok}tok" if not summarized else f"📋+🗜️ {orig_tok}→{stored_tok}"

        sum_col = f"+{sum_cost}" if sum_cost > 0 else ""
        print(f"{turn:<6} {msgs:<6} {tokens:<8} {'+' + str(delta) if delta >= 0 else str(delta):<10} {sum_col:<10} {event:<25} [{label}] {message[:35]}")

        if summarized:
            mem = get_memory()
            print(f"\n       📋 SUMMARY TRIGGERED — Memory state after summarization:")
            for idx, m in enumerate(mem.get("messages", []), 1):
                content = m.get("content", "")
                role = m.get("role", "?")
                est_tokens = (len(content) * 10) // 30
                preview = content[:80] + ("..." if len(content) > 80 else "")
                print(f"         [{idx}] {role} (~{est_tokens} tok): {preview}")
            print()

        prev_tokens = tokens

    # --- Phase 2: Filler ---
    for message in filler_messages:
        turn += 1
        response, stats = send_message(message)
        msgs = stats.get("messages_in_memory", 0)
        tokens = stats.get("estimated_tokens", 0)
        delta = tokens - prev_tokens
        summarized = stats.get("summarized_this_turn", False)
        sum_cost = stats.get("summary_tokens_used", 0)
        total_summary_tokens += sum_cost
        event = "📋 SUMMARIZED" if summarized else ""
        compressed = stats.get("response_compressed", False)
        if compressed:
            orig_tok = stats.get("response_original_tokens", 0)
            stored_tok = stats.get("response_stored_tokens", 0)
            event = f"🗜️ compressed {orig_tok}→{stored_tok}tok" if not summarized else f"📋+🗜️ {orig_tok}→{stored_tok}"

        sum_col = f"+{sum_cost}" if sum_cost > 0 else ""
        print(f"{turn:<6} {msgs:<6} {tokens:<8} {'+' + str(delta) if delta >= 0 else str(delta):<10} {sum_col:<10} {event:<25} {message[:40]}")

        if summarized:
            mem = get_memory()
            print(f"\n       📋 SUMMARY TRIGGERED — Memory state after summarization:")
            for idx, m in enumerate(mem.get("messages", []), 1):
                content = m.get("content", "")
                role = m.get("role", "?")
                est_tokens = (len(content) * 10) // 30
                preview = content[:80] + ("..." if len(content) > 80 else "")
                print(f"         [{idx}] {role} (~{est_tokens} tok): {preview}")
            print()

        prev_tokens = tokens

    # --- Phase 3: Recall ---
    print()
    print("-" * 90)
    print("RECALL TESTS")
    print("-" * 90)
    print()

    passed = 0
    for question, keyword in recall_tests:
        turn += 1
        response, stats = send_message(question)
        msgs = stats.get("messages_in_memory", 0)
        tokens = stats.get("estimated_tokens", 0)
        found = keyword in response.lower()
        status = "✅" if found else "❌"
        if found:
            passed += 1

        print(f"{turn:<6} {msgs:<6} {tokens:<8} {'':10} {status:<15} \"{question}\"")
        print(f"       {'':6} {'':6} {'':8} {'':10} {'':15} Bot: {response[:120]}")
        print()

    # =========================================================================
    # Summary
    # =========================================================================
    print_separator("RESULTS")

    mem = get_memory()
    print(f"Final state: {mem['message_count']} messages, ~{mem['estimated_tokens']} tokens in memory")
    has_summary = mem.get("has_summary", False)
    print(f"Has summary message: {'Yes 📋' if has_summary else 'No'}")
    print(f"Recall tests: {passed}/{len(recall_tests)} passed")
    print(f"Total summarization cost: ~{total_summary_tokens} extra tokens consumed by summary LLM calls")
    print()

    if has_summary:
        for m in mem.get("messages", []):
            if m.get("is_summary") or "[Conversation summary]" in m.get("content", ""):
                print("Full summary in memory:")
                print(f"  {m['content']}")
                print()
                break

    print("Fill in the observation table in your lab report:")
    print()
    print("| Turn # | Messages | Tokens in memory | Δ Tokens | Summary cost | Event | Notes |")
    print("|--------|----------|-----------------|----------|-------------|-------|-------|")
    print("| ...    | ...      | ...             | ...      | ...         | ...   | ...   |")
    print()
    print("Key observations to note:")
    print("  - At which turn did summarization first trigger?")
    print("  - How much did the token count DROP after summarization?")
    print("  - How many EXTRA tokens did the summarization call consume?")
    print("  - Total overhead: summarization uses tokens that don't appear in memory")
    print("    (the LLM processes old messages to generate the summary — that's the cost)")
    print("  - Were all 5 recall tests passed? (Compare with other scripts)")
    print()
    print("Compare with:")
    print("  - test_memory_conversation.py: tokens grow until max_messages drops them (0 extra cost)")
    print("  - test_token_trimming.py: tokens stay under budget, old msgs dropped (0 extra cost)")
    print(f"  - This script: ~{total_summary_tokens} extra tokens spent on summarization, but facts PRESERVED")


if __name__ == "__main__":
    main()
