# Agents App — API Documentation

## Base URL

```
http://localhost:8003
```

---

## Endpoints

### POST /execute

Start a crew execution. The crew runs in the background and progress can be polled via `GET /status`.

**Request:**

```http
POST /execute
Content-Type: application/json
```

**Request Body:**

| Field   | Type   | Required | Default                            | Description                          |
|---------|--------|----------|------------------------------------|--------------------------------------|
| `topic` | string | No       | `"AI and machine learning trends"` | The topic/input for the crew's tasks |

**Example Request:**

```json
{
    "topic": "Sustainable energy solutions for urban areas"
}
```

**Response:**

| Field          | Type   | Description                                    |
|----------------|--------|------------------------------------------------|
| `execution_id` | string | UUID identifying this execution (use for polling) |
| `status`       | string | Always `"started"` on success                  |

**Example Response:**

```json
{
    "execution_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "status": "started"
}
```

**Status Codes:**

| Code | Meaning                |
|------|------------------------|
| 200  | Execution started      |

**Notes:**
- The `{topic}` placeholder in agent goals and task descriptions is replaced with the provided topic value.
- Execution runs asynchronously in a background thread. Use `GET /status` to track progress.

---

### GET /status

Get the current status and logs of a crew execution.

**Request:**

```http
GET /status?execution_id=<id>
```

**Query Parameters:**

| Parameter      | Type   | Required | Description                                |
|----------------|--------|----------|--------------------------------------------|
| `execution_id` | string | Yes      | The UUID returned by `POST /execute`       |

**Example Request:**

```
GET /status?execution_id=a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Response:**

| Field    | Type        | Description                                                    |
|----------|-------------|----------------------------------------------------------------|
| `status` | string      | One of: `"running"`, `"completed"`, `"error"`                  |
| `logs`   | string[]    | Ordered list of log messages from the execution                |
| `result` | string|null | Final crew output (populated when status is `"completed"`)     |
| `error`  | string|null | Error message (populated when status is `"error"`)             |

**Example Response (running):**

```json
{
    "status": "running",
    "logs": [
        "Initializing crew execution...",
        "Loading agent definitions...",
        "Creating agent instances...",
        "  Agent created: Researcher",
        "  Agent created: Writer",
        "  Agent created: Reviewer"
    ],
    "result": null,
    "error": null
}
```

**Example Response (completed):**

```json
{
    "status": "completed",
    "logs": [
        "Initializing crew execution...",
        "Loading agent definitions...",
        "Creating agent instances...",
        "  Agent created: Researcher",
        "  Agent created: Writer",
        "  Agent created: Reviewer",
        "Loading task definitions...",
        "Creating task instances...",
        "  Task created: Research the topic: AI and machine learning trends...",
        "  Task created: Using the research provided, write a well-structured...",
        "  Task created: Review the written article about AI and machine lear...",
        "Assembling crew...",
        "Crew assembled with process type: sequential",
        "Starting crew execution...",
        "Crew execution completed successfully."
    ],
    "result": "# AI and Machine Learning Trends\n\n...",
    "error": null
}
```

**Example Response (error):**

```json
{
    "status": "error",
    "logs": [
        "Initializing crew execution...",
        "Loading agent definitions...",
        "Error: API key not configured"
    ],
    "result": null,
    "error": "API key not configured"
}
```

**Status Codes:**

| Code | Meaning                                    |
|------|--------------------------------------------|
| 200  | Status returned successfully               |
| 400  | Missing `execution_id` query parameter     |
| 404  | Execution ID not found                     |

**Error Response (400):**

```json
{
    "error": "Missing 'execution_id' query parameter"
}
```

**Error Response (404):**

```json
{
    "error": "Execution not found"
}
```

---

## Typical Usage Flow

1. **Start execution:** `POST /execute` with a topic → receive `execution_id`
2. **Poll for progress:** `GET /status?execution_id=<id>` repeatedly until `status` is `"completed"` or `"error"`
3. **Read result:** When `status` is `"completed"`, the `result` field contains the final crew output

**Example (JavaScript):**

```javascript
// Start execution
const startRes = await fetch('/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic: 'Climate change solutions' })
});
const { execution_id } = await startRes.json();

// Poll for status
const poll = setInterval(async () => {
    const statusRes = await fetch(`/status?execution_id=${execution_id}`);
    const data = await statusRes.json();
    
    if (data.status === 'completed') {
        clearInterval(poll);
        console.log('Result:', data.result);
    } else if (data.status === 'error') {
        clearInterval(poll);
        console.error('Error:', data.error);
    }
}, 2000);
```

---

## Configuration

The agents app reads configuration from `config.json` in the application root. Relevant settings:

| Key                  | Default        | Description                                |
|----------------------|----------------|--------------------------------------------|
| `crew_process_type`  | `"sequential"` | Crew execution mode: `"sequential"` or `"hierarchical"` |
| `max_iterations`     | `10`           | Maximum iterations for agent reasoning     |
| `llm_backend`        | `"ollama"`     | LLM provider: `"ollama"`, `"openai"`, or `"gemini"` |
| `llm_model`          | `"llama3.1"`     | Model name for the selected backend        |
| `integration_mode`   | `false`        | When `true`, agents use RAG and Chatbot app tools |
