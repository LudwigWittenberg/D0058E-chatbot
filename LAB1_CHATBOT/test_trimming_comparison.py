"""
Lab 1, Task 1.5 — Trimming Comparison Test

Demonstrates the difference between message-count trimming and token-based trimming.

The trick: use VERY SHORT filler messages ("yes", "ok", "thanks", "got it").
- Message-count trimming (max_messages=10): drops old messages after 10 regardless
  of size → forgets facts even though total tokens are small
- Token-based trimming (max_tokens=1500): short messages use few tokens → facts
  SURVIVE because the budget isn't exhausted

Usage:
    python test_trimming_comparison.py

Prerequisites:
    - Chatbot app running on http://localhost:8001 with server-side memory
    - LLM server running on port 11434 (n_ctx >= 4096 recommended)
    - max_messages set in web/routes.py (the script reports the current value)
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
    return 4096


CONTEXT_BUDGET = get_context_budget()


def clear_memory():
    """Clear the server-side conversation memory."""
    try:
        r = requests.post(f"{BASE_URL}/api/memory/clear")
        r.raise_for_status()
    except requests.ConnectionError:
        print("ERROR: Cannot connect to chatbot app. Is it running on port 8001?")
        sys.exit(1)


def get_memory_info():
    """Get current memory state."""
    r = requests.get(f"{BASE_URL}/api/memory")
    return r.json()


def send_message(message):
    """Send a message and return the response."""
    r = requests.post(
        f"{BASE_URL}/chat",
        json={"message": message},
        headers={"Content-Type": "application/json"},
    )
    return r.json()


def run_test():
    print("=" * 65)
    print("  Trimming Comparison Test — Short Messages vs. Fact Recall")
    print("=" * 65)
    print()
    print(f"  Context window: {CONTEXT_BUDGET} tokens")

    # Get initial memory config
    clear_memory()
    info = get_memory_info()
    max_msgs = info.get("max_messages", "?")
    print(f"  max_messages: {max_msgs}")
    print()

    # --- Phase 1: Plant 5 facts ---
    print("-" * 65)
    print("Phase 1: Planting 5 facts")
    print("-" * 65)
    print()

    facts = [
        "My name is Alice and I study at LTU.",
        "My favorite color is purple and my lucky number is 42.",
        "I am working on a 5G network slicing project.",
        "I have a cat named Pixel.",
        "My thesis deadline is March 15th.",
    ]

    for i, fact in enumerate(facts, 1):
        print(f"  [{i}] Planting: {fact[:50]}...")
        send_message(fact)

    info = get_memory_info()
    print(f"\n  After planting: {info['message_count']} msgs | ~{info['estimated_tokens']} tokens")
    print()

    # --- Phase 2: Send many SHORT filler messages ---
    print("-" * 65)
    print("Phase 2: Sending 15 very short filler messages")
    print("  (These use few tokens but many message slots)")
    print("-" * 65)
    print()

    short_fillers = [
        "ok", "yes", "thanks", "got it", "sure",
        "right", "I see", "cool", "nice", "ok thanks",
        "understood", "great", "fine", "alright", "perfect",
    ]

    for i, filler in enumerate(short_fillers, 1):
        data = send_message(filler)
        response = data.get("response", "")
        # Only show every 5th message to reduce output
        if i % 5 == 0 or i == 1:
            info = get_memory_info()
            print(f"  [{i}/15] \"{filler}\" → {info['message_count']} msgs | ~{info['estimated_tokens']} tokens")

    print()
    info = get_memory_info()
    print(f"  Final state: {info['message_count']} msgs (max {info['max_messages']}) | ~{info['estimated_tokens']} tokens")
    print()

    # --- Phase 3: Recall test ---
    print("-" * 65)
    print("Phase 3: Testing recall of planted facts")
    print("-" * 65)
    print()

    recall_questions = [
        ("What is my name and where do I study?", ["alice", "ltu"]),
        ("What is my favorite color?", ["purple"]),
        ("What project am I working on?", ["5g", "slicing"]),
        ("What is my cat's name?", ["pixel"]),
        ("When is my thesis deadline?", ["march", "15"]),
    ]

    passed = 0
    failed = 0

    for question, keywords in recall_questions:
        data = send_message(question)
        response = data.get("response", "").lower()
        is_error = response.startswith("error:")

        if is_error:
            print(f"  ⚠️  {question}")
            print(f"      ERROR: {response[:100]}")
            failed += 1
        else:
            found = [kw for kw in keywords if kw in response]
            missed = [kw for kw in keywords if kw not in response]
            if missed:
                print(f"  ❌ {question}")
                print(f"      Missing: {', '.join(missed)}")
                failed += 1
            else:
                print(f"  ✅ {question}")
                passed += 1

    # --- Summary ---
    print()
    print("=" * 65)
    print("  RESULTS")
    print("=" * 65)
    print()
    print(f"  Recall: {passed}/5 passed, {failed}/5 failed")
    print()

    info = get_memory_info()
    print(f"  Final memory: {info['message_count']} msgs (max {info['max_messages']}) | ~{info['estimated_tokens']} tokens")
    print()

    if failed == 0:
        print("  ✅ ALL FACTS REMEMBERED!")
        print("     Token-based trimming kept facts because short fillers used few tokens.")
        print("     The token budget was never exceeded, so nothing was trimmed.")
    elif passed == 0:
        print("  ❌ ALL FACTS FORGOTTEN!")
        print("     Message-count trimming dropped the early facts when filler messages")
        print("     pushed the count past max_messages — even though total tokens were low.")
    else:
        print(f"  ⚠️  PARTIAL RECALL — some facts survived, some were trimmed.")
    print()
    print("  Compare:")
    print("    • With max_messages=10 (message trimming): expects FORGETTING (❌)")
    print("    • With max_tokens=1500 (token trimming):   expects RECALL (✅)")
    print("      because 15 short fillers add very few tokens.")
    print()


if __name__ == "__main__":
    run_test()
