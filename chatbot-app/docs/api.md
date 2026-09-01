# Chatbot App — API Documentation

Base URL: `http://localhost:8001`

---

## Endpoints

### `POST /chat`

Send a chat message and receive an AI-generated response.

**Description:**
This is the primary endpoint for the chat interface. It accepts a user message along with the conversation history, passes them to the AI module, and returns the generated response.

**Request:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | Yes | The user's message text |
| `history` | array | No | Conversation history (default: `[]`) |
| `persona` | string | No | Persona name for system prompt selection (default: `"default"`) |

Each entry in `history` has the following shape:

```json
{
  "role": "user" | "assistant",
  "content": "Message text"
}
```

**Example request:**

```json
{
  "message": "What is retrieval-augmented generation?",
  "history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help you today?"}
  ]
}
```

**Response (200 OK):**

| Field | Type | Description |
|-------|------|-------------|
| `response` | string | The generated assistant response |
| `model` | string | Name of the LLM model used |
| `usage` | object | Token usage statistics |

```json
{
  "response": "Retrieval-augmented generation (RAG) is a technique that...",
  "model": "llama3.1",
  "usage": {
    "prompt_tokens": 85,
    "completion_tokens": 142,
    "total_tokens": 227
  }
}
```

**Error response (400 Bad Request):**

```json
{
  "error": "Missing 'message' field"
}
```

**Error response (500 — AI module error):**

When the AI module encounters an error, the endpoint still returns a 200 status with error details in the response field:

```json
{
  "response": "Error: LLM backend 'ollama' failed: Connection refused",
  "model": "error",
  "usage": {}
}
```

---

### `POST /api/generate`

Generate a response from a prompt. Designed for inter-application use (e.g., the Agents app calling the Chatbot for text generation).

**Description:**
This endpoint provides a simpler interface for programmatic text generation. It accepts a prompt string and optional parameters, and returns the generated text. Used by the Agents app's `ChatGenerateTool` in integrated mode.

**Request:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | string | Yes | The text prompt to generate from |
| `system_prompt` | string | No | System instructions (default: `"You are a helpful assistant."`) |
| `history` | array | No | Optional conversation context (default: `[]`) |

**Example request:**

```json
{
  "prompt": "Summarize the key benefits of microservice architecture in 3 bullet points.",
  "system_prompt": "You are a technical writer. Be concise and precise."
}
```

**Response (200 OK):**

| Field | Type | Description |
|-------|------|-------------|
| `response` | string | The generated text |
| `model` | string | Name of the LLM model used |
| `usage` | object | Token usage statistics |

```json
{
  "response": "• Independent deployment and scaling of services\n• Technology flexibility per service\n• Fault isolation — one service failure doesn't bring down the system",
  "model": "llama3.1",
  "usage": {
    "prompt_tokens": 42,
    "completion_tokens": 38,
    "total_tokens": 80
  }
}
```

**Error response (400 Bad Request):**

```json
{
  "error": "Missing 'prompt' field"
}
```

---

### `GET /`

Render the chat web interface.

**Description:**
Returns the HTML page with the chat UI. This is the main entry point for browser-based interaction.

**Response:** HTML page (Jinja2 template `web/templates/index.html`)

---

## Configuration

The chatbot app reads its configuration from `config.json` (or falls back to environment variables). Key parameters that affect API behavior:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `llm_backend` | `"ollama"` | Active LLM backend (`"ollama"`, `"openai"`, `"gemini"`) |
| `llm_model` | `"llama3.1"` | Model name to use |
| `temperature` | `0.7` | Sampling temperature (0.0–2.0) |
| `max_tokens` | `1024` | Maximum tokens in generated response |
| `system_prompt` | `"You are a helpful assistant."` | Default system prompt |
| `integration_mode` | `false` | When `true`, augments responses with RAG context |

---

## Usage Examples

### cURL

```bash
# Send a chat message
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain Python decorators"}'

# Generate text (inter-app API)
curl -X POST http://localhost:8001/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a haiku about machine learning"}'
```

### Python (requests)

```python
import requests

# Chat endpoint
response = requests.post("http://localhost:8001/chat", json={
    "message": "What is a neural network?",
    "history": []
})
print(response.json()["response"])

# Generate endpoint
response = requests.post("http://localhost:8001/api/generate", json={
    "prompt": "List 3 applications of NLP",
    "system_prompt": "Be brief and use bullet points."
})
print(response.json()["response"])
```

### JavaScript (fetch)

```javascript
// Chat endpoint
const response = await fetch('/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        message: 'How does attention work in transformers?',
        history: []
    })
});
const data = await response.json();
console.log(data.response);
```
