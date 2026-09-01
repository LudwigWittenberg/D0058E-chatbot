/**
 * Chatbot App — SERVER-SIDE MEMORY VERSION.
 *
 * === LAB 1, TASK 1.3 ===
 *
 * This file replaces the original chatbot-app/web/static/js/chat.js.
 *
 * HOW TO USE:
 *   1. Back up original:  cp chatbot-app/web/static/js/chat.js chatbot-app/web/static/js/chat_old.js
 *   2. Copy this file:    cp student_test/lab1_server_memory/chat.js chatbot-app/web/static/js/chat.js
 *
 * WHAT CHANGED (compared to chat_old.js):
 *   - REMOVED: let history = []  (no more client-side history accumulation)
 *   - REMOVED: history.push(...) calls (server stores messages now)
 *   - REMOVED: history sent in fetch body (only message is sent)
 *   - ADDED: renderMemoryStats() — displays token usage below each response
 *   - CHANGED: sendMessage() sends only { message, persona } — no history field
 *
 * WHY:
 *   The server now manages conversation memory via ConversationMemory class.
 *   The client's only job is to send the new message and display the response.
 *   This lets the server control trimming, summarization, and monitoring.
 */

(function () {
    "use strict";

    // =========================================================
    // Tab Navigation
    // =========================================================
    document.querySelectorAll(".tab-btn").forEach(function (btn) {
        btn.addEventListener("click", function () {
            document.querySelectorAll(".tab-btn").forEach(function (b) {
                b.classList.remove("active");
            });
            document.querySelectorAll(".tab-content").forEach(function (c) {
                c.classList.remove("active");
            });
            btn.classList.add("active");
            var tabId = btn.getAttribute("data-tab");
            document.getElementById(tabId).classList.add("active");
        });
    });

    // =========================================================
    // Sidebar Section Navigation (scoped to parent tab)
    // =========================================================
    document.querySelectorAll(".orch-link").forEach(function (link) {
        link.addEventListener("click", function () {
            if (link.disabled) return;
            var parentTab = link.closest(".tab-content");
            parentTab.querySelectorAll(".orch-link").forEach(function (l) {
                l.classList.remove("active");
            });
            parentTab.querySelectorAll(".orch-section").forEach(function (s) {
                s.classList.remove("active");
            });
            link.classList.add("active");
            var sectionId = link.getAttribute("data-section");
            var section = document.getElementById(sectionId);
            if (section) section.classList.add("active");
        });
    });

    // =========================================================================
    // DOM elements
    // =========================================================================
    const chatArea = document.getElementById("chat-area");
    const chatForm = document.getElementById("chat-form");
    const messageInput = document.getElementById("message-input");
    const modelSelect = document.getElementById("model-select");
    const personaSelect = document.getElementById("persona-select");
    const sendButton = chatForm.querySelector(".send-button");

    // NOTE: No "let history = []" here!
    // The old version accumulated messages in this array and sent them all
    // with each request. Now the server handles this.

    // =========================================================================
    // Persona loading (unchanged from original)
    // =========================================================================

    /**
     * Fetch available personas from the backend and populate the dropdown.
     * This is the same as the original — personas are still managed server-side.
     */
    async function loadPersonas() {
        try {
            const response = await fetch("/api/personas");
            if (response.ok) {
                const data = await response.json();
                const personas = data.personas || [];

                // Reset dropdown, keep "Default" as first option
                personaSelect.innerHTML = '<option value="">Default</option>';

                // Add each persona from the server
                personas.forEach(function (name) {
                    if (name === "default") return; // skip — already represented by ""
                    const option = document.createElement("option");
                    option.value = name;
                    // Capitalize first letter for display
                    option.textContent = name.charAt(0).toUpperCase() + name.slice(1);
                    personaSelect.appendChild(option);
                });

                // Placeholder for student-defined persona (disabled until they add it)
                const placeholder = document.createElement("option");
                placeholder.value = "my_persona";
                placeholder.textContent = "✏️ My Persona (student-defined)";
                placeholder.disabled = true;
                personaSelect.appendChild(placeholder);
            }
        } catch (err) {
            console.warn("Could not load personas:", err);
        }
    }

    // Load personas when page loads
    loadPersonas();

    // =========================================================================
    // UI rendering functions
    // =========================================================================

    /**
     * Render a message bubble in the chat area.
     * @param {"user"|"assistant"} role - Who sent the message.
     * @param {string} content - The message text.
     */
    function renderMessage(role, content) {
        // Remove the welcome message on first interaction
        const welcome = chatArea.querySelector(".welcome-message");
        if (welcome) welcome.remove();

        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", role);

        const label = document.createElement("div");
        label.classList.add("message-label");
        label.textContent = role === "user" ? "You" : "Assistant";

        const bubble = document.createElement("div");
        bubble.classList.add("message-bubble");
        bubble.textContent = content;

        messageDiv.appendChild(label);
        messageDiv.appendChild(bubble);
        chatArea.appendChild(messageDiv);

        scrollToBottom();
    }

    /**
     * === NEW: Render memory statistics below the assistant's response ===
     *
     * Shows how many messages are in memory, estimated token count,
     * and what percentage of the 4096-token budget is used.
     *
     * This helps you OBSERVE how context grows with each message.
     * When budget_used_pct approaches 100%, the model will start
     * losing context or producing errors.
     *
     * @param {object} stats - memory_stats from the server response
     */
    function renderMemoryStats(stats) {
        if (!stats) return;

        const statsDiv = document.createElement("div");
        statsDiv.classList.add("memory-stats");

        // Color-code based on budget usage
        let color = "#6c757d"; // gray (normal)
        if (stats.budget_used_pct > 75) color = "#dc3545"; // red (danger)
        else if (stats.budget_used_pct > 50) color = "#fd7e14"; // orange (warning)

        statsDiv.innerHTML =
            `<small style="color: ${color}">` +
            `📊 Memory: ${stats.messages_in_memory} msgs | ` +
            `~${stats.estimated_tokens} tokens | ` +
            `${stats.budget_used_pct}% of ${stats.context_budget} budget` +
            `</small>`;

        chatArea.appendChild(statsDiv);
        scrollToBottom();
    }

    /**
     * Show a typing indicator (animated dots) while waiting for response.
     * @returns {HTMLElement} The indicator element (removed when response arrives).
     */
    function showTypingIndicator() {
        const indicator = document.createElement("div");
        indicator.classList.add("typing-indicator");
        indicator.innerHTML = "<span></span><span></span><span></span>";
        chatArea.appendChild(indicator);
        scrollToBottom();
        return indicator;
    }

    /**
     * Auto-scroll the chat area to show the latest message.
     */
    function scrollToBottom() {
        chatArea.scrollTop = chatArea.scrollHeight;
    }

    // =========================================================================
    // === CHANGED: Message sending — NO history sent to server ===
    // =========================================================================

    /**
     * Send a message to the /chat endpoint.
     *
     * === KEY DIFFERENCE FROM ORIGINAL ===
     * Original: body: JSON.stringify({ message, history })  ← sent ALL messages
     * This version: body: JSON.stringify({ message })       ← only new message
     *
     * The server retrieves history from its own ConversationMemory.
     * The server also stores this message + the response automatically.
     *
     * @param {string} message - The user's message text.
     */
    async function sendMessage(message) {
        // Display the user's message in the UI
        renderMessage("user", message);

        // Disable input while waiting for response
        messageInput.disabled = true;
        sendButton.disabled = true;

        const indicator = showTypingIndicator();

        try {
            // Build the request payload
            // NOTE: Only "message" is sent — NO "history" field!
            // The server manages history via ConversationMemory.
            const payload = { message: message };

            // Include persona if one is selected in the dropdown
            const selectedPersona = personaSelect.value;
            if (selectedPersona) {
                payload.persona = selectedPersona;
            }

            // Send to server
            const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
                // ^ Compare with original: JSON.stringify({ message, history })
            });

            const data = await response.json();
            indicator.remove();

            if (response.ok && data.response) {
                // Display the assistant's response
                renderMessage("assistant", data.response);

                // === NEW: Show memory stats below the response ===
                // This lets you watch context grow in real-time
                renderMemoryStats(data.memory_stats);

                // NOTE: No history.push() here!
                // The old version did: history.push({ role: "assistant", content: data.response })
                // Now the server handles this in routes.py: _memory.add_message(...)
            } else {
                const errorText = data.error || "An unexpected error occurred.";
                renderMessage("assistant", "Error: " + errorText);
            }
        } catch (err) {
            indicator.remove();
            renderMessage("assistant", "Error: Could not connect to the server.");
        } finally {
            // Re-enable input
            messageInput.disabled = false;
            sendButton.disabled = false;
            messageInput.focus();
        }
    }

    // =========================================================================
    // Event handlers (unchanged)
    // =========================================================================

    // Form submit — send the message
    chatForm.addEventListener("submit", function (e) {
        e.preventDefault();
        const message = messageInput.value.trim();
        if (!message) return;
        messageInput.value = "";
        sendMessage(message);
    });

    // Model selector (informational only in this version)
    modelSelect.addEventListener("change", function () {
        console.log("Model changed to:", modelSelect.value);
    });

    // Focus input on page load
    messageInput.focus();
})();
