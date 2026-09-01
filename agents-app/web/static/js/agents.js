/**
 * Agents App — Vanilla JS with tab navigation and crew execution.
 *
 * Handles tab switching, crew execution triggering, progress polling,
 * log rendering, and output display.
 */

(function () {
    "use strict";

    // =========================================================
    // Tab Navigation
    // =========================================================
    document.querySelectorAll(".tab-btn").forEach(function (btn) {
        btn.addEventListener("click", function () {
            // Deactivate all tabs and content
            document.querySelectorAll(".tab-btn").forEach(function (b) {
                b.classList.remove("active");
            });
            document.querySelectorAll(".tab-content").forEach(function (c) {
                c.classList.remove("active");
            });
            // Activate clicked tab and its content
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
            // Ignore disabled buttons
            if (link.disabled) return;
            // Find the parent tab content container
            var parentTab = link.closest(".tab-content");
            // Deactivate only links and sections within THIS tab
            parentTab.querySelectorAll(".orch-link").forEach(function (l) {
                l.classList.remove("active");
            });
            parentTab.querySelectorAll(".orch-section").forEach(function (s) {
                s.classList.remove("active");
            });
            // Activate clicked link and its section
            link.classList.add("active");
            var sectionId = link.getAttribute("data-section");
            var section = document.getElementById(sectionId);
            section.classList.add("active");
        });
    });

    // =========================================================
    // Agents Tab — Refresh Button
    // =========================================================
    var refreshAgentsBtn = document.getElementById("refresh-agents-btn");
    if (refreshAgentsBtn) {
        refreshAgentsBtn.addEventListener("click", async function () {
            refreshAgentsBtn.disabled = true;
            refreshAgentsBtn.textContent = "⏳ Loading...";

            try {
                var response = await fetch("/api/agents");
                var data = await response.json();

                var grid = document.getElementById("agents-grid");
                if (!grid) return;

                if (data.agents && data.agents.length > 0) {
                    grid.innerHTML = "";
                    data.agents.forEach(function (agent) {
                        var card = document.createElement("div");
                        card.className = "agent-card";
                        card.setAttribute("data-role", agent.role);

                        var toolsHtml = "";
                        if (agent.tools && agent.tools.length > 0) {
                            toolsHtml =
                                '<div class="agent-field">' +
                                '<span class="field-label">Tools:</span>' +
                                '<p class="field-value">' + agent.tools.join(", ") + "</p>" +
                                "</div>";
                        }

                        card.innerHTML =
                            '<div class="agent-card-header">' +
                            '<span class="agent-icon" aria-hidden="true">🤖</span>' +
                            '<h3 class="agent-role">' + agent.role + "</h3>" +
                            "</div>" +
                            '<div class="agent-card-body">' +
                            '<div class="agent-field">' +
                            '<span class="field-label">Goal:</span>' +
                            '<p class="field-value">' + agent.goal + "</p>" +
                            "</div>" +
                            '<div class="agent-field">' +
                            '<span class="field-label">Backstory:</span>' +
                            '<p class="field-value">' + agent.backstory + "</p>" +
                            "</div>" +
                            toolsHtml +
                            "</div>";

                        grid.appendChild(card);
                    });
                } else {
                    grid.innerHTML =
                        '<div class="placeholder-card"><p>No agents defined yet. Implement <code>ai/agents.py</code> to see agent cards here.</p></div>';
                }
            } catch (err) {
                console.error("Failed to refresh agents:", err);
            } finally {
                refreshAgentsBtn.disabled = false;
                refreshAgentsBtn.textContent = "🔄 Refresh";
            }
        });
    }

    // =========================================================
    // Tasks Tab — Refresh Button
    // =========================================================
    var refreshTasksBtn = document.getElementById("refresh-tasks-btn");
    if (refreshTasksBtn) {
        refreshTasksBtn.addEventListener("click", async function () {
            refreshTasksBtn.disabled = true;
            refreshTasksBtn.textContent = "⏳ Loading...";

            try {
                var response = await fetch("/api/tasks");
                var data = await response.json();

                var container = document.getElementById("pipeline-container");
                if (!container) return;

                if (data.tasks && data.tasks.length > 0) {
                    container.innerHTML = "";
                    data.tasks.forEach(function (task, index) {
                        if (index > 0) {
                            var connector = document.createElement("div");
                            connector.className = "step-connector";
                            connector.setAttribute("aria-hidden", "true");
                            connector.innerHTML = '<span class="connector-arrow">↓</span>';
                            container.appendChild(connector);
                        }

                        var step = document.createElement("div");
                        step.className = "pipeline-step";
                        step.setAttribute("data-agent", task.agent_role);

                        var expectedHtml = "";
                        if (task.expected_output) {
                            expectedHtml =
                                '<div class="step-expected">' +
                                '<span class="field-label">Expected output:</span>' +
                                '<p class="field-value">' + task.expected_output + "</p></div>";
                        }

                        step.innerHTML =
                            '<div class="step-header">' +
                            '<div class="step-number">' + (index + 1) + "</div>" +
                            '<span class="step-agent">' + task.agent_role + "</span>" +
                            "</div>" +
                            '<div class="step-content">' +
                            '<p class="step-description">' + task.description + "</p>" +
                            expectedHtml +
                            "</div>";

                        container.appendChild(step);
                    });
                } else {
                    container.innerHTML =
                        '<div class="placeholder-card"><p>No tasks defined yet. Implement <code>ai/tasks.py</code> to see the pipeline here.</p></div>';
                }
            } catch (err) {
                console.error("Failed to refresh tasks:", err);
            } finally {
                refreshTasksBtn.disabled = false;
                refreshTasksBtn.textContent = "🔄 Refresh";
            }
        });
    }

    // =========================================================
    // Crew Execution
    // =========================================================

    // Init Crew button
    var initCrewBtn = document.getElementById("init-crew-btn");
    var initStatus = document.getElementById("init-status");
    var initLogContainer = document.getElementById("init-log-container");

    if (initCrewBtn) {
        initCrewBtn.addEventListener("click", async function () {
            initCrewBtn.disabled = true;
            initCrewBtn.textContent = "⏳ Initializing...";
            if (initStatus) initStatus.textContent = "";
            if (initLogContainer) initLogContainer.innerHTML = "";

            try {
                var response = await fetch("/api/crew/init", { method: "POST" });
                var data = await response.json();

                // Display logs
                if (initLogContainer && data.logs) {
                    data.logs.forEach(function (msg) {
                        var entry = document.createElement("div");
                        entry.classList.add("log-entry", "info");
                        var ts = document.createElement("span");
                        ts.classList.add("log-timestamp");
                        ts.textContent = new Date().toLocaleTimeString();
                        entry.appendChild(ts);
                        entry.appendChild(document.createTextNode(msg));
                        initLogContainer.appendChild(entry);
                    });
                }

                if (data.status === "ok") {
                    if (initStatus) {
                        initStatus.textContent = "✓ Crew initialized successfully";
                        initStatus.style.color = "#10b981";
                    }
                    // Enable the "Run Crew" sidebar topic
                    document.querySelectorAll(".crew-requires-init").forEach(function (btn) {
                        btn.disabled = false;
                    });
                } else {
                    if (initStatus) {
                        initStatus.textContent = "✗ " + (data.error || "Initialization failed");
                        initStatus.style.color = "#ef4444";
                    }
                }
            } catch (err) {
                if (initStatus) {
                    initStatus.textContent = "✗ Network error";
                    initStatus.style.color = "#ef4444";
                }
            } finally {
                initCrewBtn.disabled = false;
                initCrewBtn.textContent = "🔧 Initialize Crew";
            }
        });
    }

    // DOM elements for crew execution
    var executeBtn = document.getElementById("execute-btn");
    var topicInput = document.getElementById("topic-input");
    var logContainer = document.getElementById("log-container");
    var outputContainer = document.getElementById("output-container");

    // Polling state
    var currentExecutionId = null;
    var pollInterval = null;

    /**
     * Clear the log container and show a fresh state.
     */
    function clearLog() {
        if (logContainer) logContainer.innerHTML = "";
    }

    /**
     * Add a log entry to the log container.
     * @param {string} message - The log message text.
     * @param {"info"|"success"|"error"|"warning"} [type="info"] - Log entry type for styling.
     */
    function addLogEntry(message, type) {
        if (!logContainer) return;
        type = type || "info";

        // Remove placeholder if present
        var placeholder = logContainer.querySelector(".log-placeholder");
        if (placeholder) {
            placeholder.remove();
        }

        var entry = document.createElement("div");
        entry.classList.add("log-entry", type);

        var timestamp = document.createElement("span");
        timestamp.classList.add("log-timestamp");
        timestamp.textContent = new Date().toLocaleTimeString();

        entry.appendChild(timestamp);
        entry.appendChild(document.createTextNode(message));
        logContainer.appendChild(entry);

        // Auto-scroll to bottom
        logContainer.scrollTop = logContainer.scrollHeight;
    }

    /**
     * Set the output display content.
     * @param {string} content - The output text to display.
     * @param {boolean} [isError=false] - Whether this is an error message.
     */
    function setOutput(content, isError) {
        if (!outputContainer) return;
        isError = isError || false;
        outputContainer.innerHTML = "";

        var el = document.createElement("div");
        el.classList.add(isError ? "output-error" : "output-content");
        el.textContent = content;
        outputContainer.appendChild(el);
    }

    /**
     * Clear the output display.
     */
    function clearOutput() {
        if (!outputContainer) return;
        outputContainer.innerHTML =
            '<p class="output-placeholder">Crew output will appear here after execution completes.</p>';
    }

    /**
     * Start a crew execution by calling POST /api/crew/run.
     */
    async function startExecution() {
        var topic = topicInput.value.trim();
        if (!topic) {
            topic = "AI and machine learning trends";
        }

        // Clear agent log panels and output
        var logsContainer = document.getElementById("agent-logs-container");
        if (logsContainer) logsContainer.innerHTML = "";
        clearOutput();
        executeBtn.disabled = true;
        executeBtn.textContent = "⏳ Running...";

        // Track agent panels
        var agentPanels = {}; // agentName → DOM container element

        function getOrCreateAgentPanel(agentName) {
            if (agentPanels[agentName]) return agentPanels[agentName];
            // Create a new panel for this agent
            var panel = document.createElement("div");
            panel.className = "agent-log-panel active-agent";
            panel.innerHTML =
                '<div class="agent-log-header">' +
                '<span class="agent-log-dot"></span>' +
                '<span class="agent-log-title">' + agentName + '</span>' +
                '</div>' +
                '<div class="log-container agent-log-container" role="log"></div>';
            logsContainer.appendChild(panel);
            agentPanels[agentName] = {
                panel: panel,
                container: panel.querySelector(".agent-log-container"),
            };
            return agentPanels[agentName];
        }

        function addToAgentLog(agentName, message, type) {
            var p = getOrCreateAgentPanel(agentName);
            var entry = document.createElement("div");
            entry.classList.add("log-entry", type || "info");
            var ts = document.createElement("span");
            ts.classList.add("log-timestamp");
            ts.textContent = new Date().toLocaleTimeString();
            entry.appendChild(ts);
            entry.appendChild(document.createTextNode(message));
            p.container.appendChild(entry);
            p.container.scrollTop = p.container.scrollHeight;
        }

        function markAgentComplete(agentName) {
            var p = agentPanels[agentName];
            if (p) {
                p.panel.classList.remove("active-agent");
                p.panel.classList.add("completed-agent");
            }
        }

        try {
            var response = await fetch("/api/crew/run", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ topic: topic }),
            });

            var data = await response.json();

            if (response.ok && data.execution_id) {
                currentExecutionId = data.execution_id;

                // Poll and route to agent panels
                var renderedLogCount = 0;
                var currentAgent = null;

                pollInterval = setInterval(async function () {
                    if (!currentExecutionId) { stopPolling(); return; }
                    try {
                        var resp = await fetch("/status?execution_id=" + encodeURIComponent(currentExecutionId));
                        var statusData = await resp.json();
                        if (!resp.ok) { stopPolling(); resetButton(); return; }

                        if (statusData.logs && statusData.logs.length > renderedLogCount) {
                            for (var i = renderedLogCount; i < statusData.logs.length; i++) {
                                var msg = statusData.logs[i];

                                // Detect agent from Communication round header
                                var commMatch = msg.match(/\[Communication round #\d+ for Agent: ([^\]]+)\]/);
                                if (commMatch) {
                                    currentAgent = commMatch[1];
                                    addToAgentLog(currentAgent, msg, "info");
                                    continue;
                                }

                                // Detect task done
                                var taskMatch = msg.match(/\[TASK_DONE:([^\]]+)\]/);
                                if (taskMatch) {
                                    var doneAgent = taskMatch[1];
                                    addToAgentLog(doneAgent, "✓ Task completed", "success");
                                    markAgentComplete(doneAgent);
                                    currentAgent = null;
                                    continue;
                                }

                                // LLM call/response
                                if (msg.indexOf("[LLM_CALL") !== -1) {
                                    if (currentAgent) {
                                        addToAgentLog(currentAgent, msg, "info");
                                    }
                                    continue;
                                }

                                if (msg.indexOf("[LLM_RESPONSE") !== -1) {
                                    if (currentAgent) {
                                        addToAgentLog(currentAgent, msg, "warning");
                                    }
                                    continue;
                                }

                                // All other messages go to current agent
                                if (currentAgent) {
                                    addToAgentLog(currentAgent, msg, "info");
                                }
                            }
                            renderedLogCount = statusData.logs.length;
                        }

                        // Check completion
                        if (statusData.status === "completed") {
                            if (statusData.result) {
                                setOutput(statusData.result, false);
                            }
                            // Enable "Reflect on Agent Responses" topic
                            document.querySelectorAll(".crew-requires-run").forEach(function (btn) {
                                btn.disabled = false;
                            });
                            stopPolling();
                            resetButton();
                        } else if (statusData.status === "error") {
                            setOutput(statusData.error || "An error occurred.", true);
                            stopPolling();
                            resetButton();
                        }
                    } catch (err) {
                        stopPolling();
                        resetButton();
                    }
                }, 1000);

            } else {
                setOutput(data.error || "Failed to start execution.", true);
                resetButton();
            }
        } catch (err) {
            setOutput("Could not connect to the server.", true);
            resetButton();
        }
    }

    /**
     * Stop the polling interval.
     */
    function stopPolling() {
        if (pollInterval) {
            clearInterval(pollInterval);
            pollInterval = null;
        }
    }

    /**
     * Reset the execute button to its default state.
     */
    function resetButton() {
        if (executeBtn) {
            executeBtn.disabled = false;
            executeBtn.textContent = "Run Crew";
        }
    }

    // Event listeners
    if (executeBtn) {
        executeBtn.addEventListener("click", function () {
            startExecution();
        });
    }

    if (topicInput) {
        topicInput.addEventListener("keydown", function (e) {
            if (e.key === "Enter") {
                e.preventDefault();
                startExecution();
            }
        });
    }

    // =========================================================
    // Reflect on Agent Responses
    // =========================================================
    var loadResponsesBtn = document.getElementById("load-responses-btn");
    var clearResponsesBtn = document.getElementById("clear-responses-btn");
    var responsesContainer = document.getElementById("responses-container");

    if (loadResponsesBtn) {
        loadResponsesBtn.addEventListener("click", async function () {
            loadResponsesBtn.disabled = true;
            loadResponsesBtn.textContent = "⏳ Loading...";
            try {
                var response = await fetch("/api/crew/responses");
                var data = await response.json();

                if (!responsesContainer) return;
                responsesContainer.innerHTML = "";

                if (data.responses && data.responses.length > 0) {
                    data.responses.forEach(function (item, idx) {
                        var card = document.createElement("div");
                        card.className = "response-card";
                        var header = document.createElement("div");
                        header.className = "response-card-header";
                        header.textContent = (idx + 1) + ". " + item.filename;
                        var body = document.createElement("pre");
                        body.className = "response-card-body";
                        body.textContent = item.content;
                        card.appendChild(header);
                        card.appendChild(body);
                        responsesContainer.appendChild(card);
                    });
                } else {
                    responsesContainer.innerHTML = '<p class="log-placeholder">No response files found. Run the crew first.</p>';
                }
            } catch (err) {
                responsesContainer.innerHTML = '<p class="log-placeholder">Error loading responses.</p>';
            } finally {
                loadResponsesBtn.disabled = false;
                loadResponsesBtn.textContent = "📄 Load Responses";
            }
        });
    }

    if (clearResponsesBtn) {
        clearResponsesBtn.addEventListener("click", async function () {
            try {
                await fetch("/api/crew/responses/clear", { method: "POST" });
                if (responsesContainer) {
                    responsesContainer.innerHTML = '<p class="log-placeholder">Files cleared.</p>';
                }
            } catch (err) {}
        });
    }

    // =========================================================
    // CrewAI with Tools Tab (mirrors crew-tab with different IDs)
    // =========================================================
    var initCrewToolsBtn = document.getElementById("init-crew-tools-btn");
    var initToolsStatus = document.getElementById("init-tools-status");
    var initToolsLogContainer = document.getElementById("init-tools-log-container");

    if (initCrewToolsBtn) {
        initCrewToolsBtn.addEventListener("click", async function () {
            initCrewToolsBtn.disabled = true;
            initCrewToolsBtn.textContent = "⏳ Checking tools...";
            if (initToolsStatus) initToolsStatus.textContent = "";
            if (initToolsLogContainer) initToolsLogContainer.innerHTML = "";

            // Check if tools are implemented before proceeding
            try {
                var checkResp = await fetch("/api/crew/check-tools");
                var checkData = await checkResp.json();
                if (!checkData.tools_available) {
                    if (initToolsStatus) {
                        initToolsStatus.textContent = "✗ Tools not implemented yet! Complete Task 3.5 first.";
                        initToolsStatus.style.color = "#ef4444";
                    }
                    if (initToolsLogContainer) {
                        var entry = document.createElement("div");
                        entry.classList.add("log-entry", "error");
                        entry.textContent = "Error: WordCountTool not found in ai/tools.py. You need to implement custom tools (Task 3.5) before using this tab. Use the '⚡ The CrewAI in Action' tab for the default crew without tools.";
                        initToolsLogContainer.appendChild(entry);
                    }
                    initCrewToolsBtn.disabled = false;
                    initCrewToolsBtn.textContent = "🔧 Initialize Crew";
                    return;
                }
            } catch (e) {}

            initCrewToolsBtn.textContent = "⏳ Initializing...";

            try {
                var response = await fetch("/api/crew/init", { method: "POST" });
                var data = await response.json();

                if (initToolsLogContainer && data.logs) {
                    data.logs.forEach(function (msg) {
                        var entry = document.createElement("div");
                        entry.classList.add("log-entry", "info");
                        var ts = document.createElement("span");
                        ts.classList.add("log-timestamp");
                        ts.textContent = new Date().toLocaleTimeString();
                        entry.appendChild(ts);
                        entry.appendChild(document.createTextNode(msg));
                        initToolsLogContainer.appendChild(entry);
                    });
                }

                if (data.status === "ok") {
                    if (initToolsStatus) {
                        initToolsStatus.textContent = "✓ Crew initialized successfully";
                        initToolsStatus.style.color = "#10b981";
                    }
                    document.querySelectorAll(".crew-tools-requires-init").forEach(function (btn) {
                        btn.disabled = false;
                    });
                } else {
                    if (initToolsStatus) {
                        initToolsStatus.textContent = "✗ " + (data.error || "Initialization failed");
                        initToolsStatus.style.color = "#ef4444";
                    }
                }
            } catch (err) {
                if (initToolsStatus) {
                    initToolsStatus.textContent = "✗ Network error";
                    initToolsStatus.style.color = "#ef4444";
                }
            } finally {
                initCrewToolsBtn.disabled = false;
                initCrewToolsBtn.textContent = "🔧 Initialize Crew";
            }
        });
    }

    // Execute crew (tools tab)
    var executeToolsBtn = document.getElementById("execute-tools-btn");
    var topicToolsInput = document.getElementById("topic-tools-input");
    var outputToolsContainer = document.getElementById("output-tools-container");

    var currentToolsExecutionId = null;
    var toolsPollInterval = null;

    function setToolsOutput(content, isError) {
        if (!outputToolsContainer) return;
        outputToolsContainer.innerHTML = "";
        var el = document.createElement("div");
        el.classList.add(isError ? "output-error" : "output-content");
        el.textContent = content;
        outputToolsContainer.appendChild(el);
    }

    function resetToolsButton() {
        if (executeToolsBtn) {
            executeToolsBtn.disabled = false;
            executeToolsBtn.textContent = "🚀 Run Crew";
        }
    }

    function stopToolsPolling() {
        if (toolsPollInterval) {
            clearInterval(toolsPollInterval);
            toolsPollInterval = null;
        }
    }

    async function startToolsExecution() {
        var topic = topicToolsInput.value.trim();
        if (!topic) topic = "AI and machine learning trends";

        var logsContainer = document.getElementById("agent-tools-logs-container");
        if (logsContainer) logsContainer.innerHTML = "";
        if (outputToolsContainer) {
            outputToolsContainer.innerHTML =
                '<p class="output-placeholder">Crew output will appear here after execution completes.</p>';
        }
        executeToolsBtn.disabled = true;
        executeToolsBtn.textContent = "⏳ Running...";

        var agentPanels = {};

        function getOrCreateAgentPanel(agentName) {
            if (agentPanels[agentName]) return agentPanels[agentName];
            var panel = document.createElement("div");
            panel.className = "agent-log-panel active-agent";
            panel.innerHTML =
                '<div class="agent-log-header">' +
                '<span class="agent-log-dot"></span>' +
                '<span class="agent-log-title">' + agentName + '</span>' +
                '</div>' +
                '<div class="log-container agent-log-container" role="log"></div>';
            logsContainer.appendChild(panel);
            agentPanels[agentName] = {
                panel: panel,
                container: panel.querySelector(".agent-log-container"),
            };
            return agentPanels[agentName];
        }

        function addToAgentLog(agentName, message, type) {
            var p = getOrCreateAgentPanel(agentName);
            var entry = document.createElement("div");
            entry.classList.add("log-entry", type || "info");
            var ts = document.createElement("span");
            ts.classList.add("log-timestamp");
            ts.textContent = new Date().toLocaleTimeString();
            entry.appendChild(ts);
            entry.appendChild(document.createTextNode(message));
            p.container.appendChild(entry);
            p.container.scrollTop = p.container.scrollHeight;
        }

        function markAgentComplete(agentName) {
            var p = agentPanels[agentName];
            if (p) {
                p.panel.classList.remove("active-agent");
                p.panel.classList.add("completed-agent");
            }
        }

        try {
            var response = await fetch("/api/crew/run", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ topic: topic }),
            });

            var data = await response.json();

            if (response.ok && data.execution_id) {
                currentToolsExecutionId = data.execution_id;
                var renderedLogCount = 0;
                var currentAgent = null;

                toolsPollInterval = setInterval(async function () {
                    if (!currentToolsExecutionId) { stopToolsPolling(); return; }
                    try {
                        var resp = await fetch("/status?execution_id=" + encodeURIComponent(currentToolsExecutionId));
                        var statusData = await resp.json();
                        if (!resp.ok) { stopToolsPolling(); resetToolsButton(); return; }

                        if (statusData.logs && statusData.logs.length > renderedLogCount) {
                            for (var i = renderedLogCount; i < statusData.logs.length; i++) {
                                var msg = statusData.logs[i];

                                var commMatch = msg.match(/\[Communication round #\d+ for Agent: ([^\]]+)\]/);
                                if (commMatch) {
                                    currentAgent = commMatch[1];
                                    addToAgentLog(currentAgent, msg, "info");
                                    continue;
                                }

                                var taskMatch = msg.match(/\[TASK_DONE:([^\]]+)\]/);
                                if (taskMatch) {
                                    var doneAgent = taskMatch[1];
                                    addToAgentLog(doneAgent, "✓ Task completed", "success");
                                    markAgentComplete(doneAgent);
                                    currentAgent = null;
                                    continue;
                                }

                                if (msg.indexOf("[TOOL_CALL:") !== -1 || msg.indexOf("[TOOL_RESULT:") !== -1) {
                                    if (currentAgent) {
                                        addToAgentLog(currentAgent, msg, "tool");
                                    }
                                    continue;
                                }

                                if (msg.indexOf("[LLM_RESPONSE") !== -1) {
                                    if (currentAgent) {
                                        addToAgentLog(currentAgent, msg, "warning");
                                    }
                                    continue;
                                }

                                if (currentAgent) {
                                    addToAgentLog(currentAgent, msg, "info");
                                }
                            }
                            renderedLogCount = statusData.logs.length;
                        }

                        if (statusData.status === "completed") {
                            if (statusData.result) {
                                setToolsOutput(statusData.result, false);
                            }
                            document.querySelectorAll(".crew-tools-requires-run").forEach(function (btn) {
                                btn.disabled = false;
                            });
                            stopToolsPolling();
                            resetToolsButton();
                        } else if (statusData.status === "error") {
                            setToolsOutput(statusData.error || "An error occurred.", true);
                            stopToolsPolling();
                            resetToolsButton();
                        }
                    } catch (err) {
                        stopToolsPolling();
                        resetToolsButton();
                    }
                }, 1000);

            } else {
                setToolsOutput(data.error || "Failed to start execution.", true);
                resetToolsButton();
            }
        } catch (err) {
            setToolsOutput("Could not connect to the server.", true);
            resetToolsButton();
        }
    }

    if (executeToolsBtn) {
        executeToolsBtn.addEventListener("click", function () {
            startToolsExecution();
        });
    }

    if (topicToolsInput) {
        topicToolsInput.addEventListener("keydown", function (e) {
            if (e.key === "Enter") {
                e.preventDefault();
                startToolsExecution();
            }
        });
    }

    // Reflect (tools tab)
    var loadToolsResponsesBtn = document.getElementById("load-tools-responses-btn");
    var clearToolsResponsesBtn = document.getElementById("clear-tools-responses-btn");
    var toolsResponsesContainer = document.getElementById("tools-responses-container");

    if (loadToolsResponsesBtn) {
        loadToolsResponsesBtn.addEventListener("click", async function () {
            loadToolsResponsesBtn.disabled = true;
            loadToolsResponsesBtn.textContent = "⏳ Loading...";
            try {
                var response = await fetch("/api/crew/responses");
                var data = await response.json();

                if (!toolsResponsesContainer) return;
                toolsResponsesContainer.innerHTML = "";

                if (data.responses && data.responses.length > 0) {
                    data.responses.forEach(function (item, idx) {
                        var card = document.createElement("div");
                        card.className = "response-card";
                        var header = document.createElement("div");
                        header.className = "response-card-header";
                        header.textContent = (idx + 1) + ". " + item.filename;
                        var body = document.createElement("pre");
                        body.className = "response-card-body";
                        body.textContent = item.content;
                        card.appendChild(header);
                        card.appendChild(body);
                        toolsResponsesContainer.appendChild(card);
                    });
                } else {
                    toolsResponsesContainer.innerHTML = '<p class="log-placeholder">No response files found. Run the crew first.</p>';
                }
            } catch (err) {
                toolsResponsesContainer.innerHTML = '<p class="log-placeholder">Error loading responses.</p>';
            } finally {
                loadToolsResponsesBtn.disabled = false;
                loadToolsResponsesBtn.textContent = "📄 Load Responses";
            }
        });
    }

    if (clearToolsResponsesBtn) {
        clearToolsResponsesBtn.addEventListener("click", async function () {
            try {
                await fetch("/api/crew/responses/clear", { method: "POST" });
                if (toolsResponsesContainer) {
                    toolsResponsesContainer.innerHTML = '<p class="log-placeholder">Files cleared.</p>';
                }
            } catch (err) {}
        });
    }
})();
