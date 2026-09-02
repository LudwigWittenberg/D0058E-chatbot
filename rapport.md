# Rapport Lab 1 - Chatbot

## Task 1.1

### Step 1

I modified the base promt to include the following instructions: `Return the answer as plain string without any formatting.` This is just to make my work easier, so I don't have to remove the formatting from the answer.

#### Prompt

```bash
curl.exe -s http://localhost:11434/api/chat -d '{
  "model": "llama3.2:3b",
  "messages": [
    {"role": "system", "content": "You are a helpful programming tutor. Return the answer as plain string without any formatting."},
    {"role": "user", "content": "What is a variable in Python?"}
  ],
  "stream": false
}'
```

#### Answer

```json
{
  "model": "llama3.2:3b",
  "created_at": "2026-09-02T16:59:50.4494626Z",
  "message": {
    "role": "assistant",
    "content": "A variable in Python is a name given to a value that can be changed during the execution of the program. Variables are used to store and manipulate data in a program."
  },
  "done": true,
  "done_reason": "stop",
  "total_duration": 4817227000,
  "load_duration": 2151491300,
  "prompt_eval_count": 49,
  "prompt_eval_duration": 593847000,
  "eval_count": 35,
  "eval_duration": 2066484000
}
```

### Step 2

#### Prompt

```bash
curl.exe -s http://localhost:11434/api/chat -d '{
  "model": "llama3.2:3b",
  "messages": [
    {"role": "system", "content": "You are a helpful programming tutor. Return the answer as plain string without any formatting."},
    {"role": "user", "content": "What is a variable in Python?"},
    {"role": "assistant", "content": "A variable in Python is a name given to a value that can be changed during the execution of the program. Variables are used to store and manipulate data in a program."},
    {"role": "user", "content": "Show me a simple example"}
  ],
  "stream": false
}'
```

#### Answer

```json
{
  "model": "llama3.2:3b",
  "created_at": "2026-09-02T17:02:38.9641465Z",
  "message": {
    "role": "assistant",
    "content": "x = 5  # assigns the value 5 to the variable x\nprint(x)  # prints 5"
  },
  "done": true,
  "done_reason": "stop",
  "total_duration": 1613466900,
  "load_duration": 5219300,
  "prompt_eval_count": 98,
  "prompt_eval_duration": 270619000,
  "eval_count": 25,
  "eval_duration": 1324445000
}
```

### Step 3

#### Prompt

```bash
curl.exe -s http://localhost:11434/api/chat -d '{
  "model": "llama3.2:3b",
  "messages": [
    {"role": "user", "content": "Show me a simple example"}
  ],
  "stream": false
}'
```

#### Answer

```json
{
  "model": "llama3.2:3b",
  "created_at": "2026-09-02T17:04:05.654799Z",
  "message": {
    "role": "assistant",
    "content": "Here's a simple example of a Python program that calculates the area of a rectangle:\n\n```\n# Define the length and width of the rectangle\nlength = float(input(\"Enter the length of the rectangle: \"))\nwidth = float(input(\"Enter the width of the rectangle: \"))\n\n# Calculate the area of the rectangle\narea = length * width\n\n# Print the result\nprint(\"The area of the rectangle is:\", area)\n```\n\nThis program prompts the user to enter the length and width of a rectangle, then calculates and prints the area of the rectangle."
  },
  "done": true,
  "done_reason": "stop",
  "total_duration": 6507872100,
  "load_duration": 7591600,
  "prompt_eval_count": 30,
  "prompt_eval_duration": 273876000,
  "eval_count": 114,
  "eval_duration": 6218854000
}
```

### Reflection questions

#### Why must you send the entire conversation history with each request?

I think its quite clear why we need to send the history of our current conversation. Without context the AI in this case dosent now what we are talking about or chated about before. Example if I go to a bakery and just say "Whats the price?" The person behind the counter would have no idea what I mean so he would just give me a price. But if were having a conversation about a cookie and I ask "Whats the price?" then he would know what I mean. So the AI needs to know the context of the conversation to give a relevant answer.

#### What would happen if you omitted the assistant's previous response from the array?

It will probably just explaine the first question again and then also include an example of the question.

#### How does this relate to the concept of "context window" (max tokens)?

This is also quite clear. The context window is the amount of tokens the AI can remember. For example it can remeber the last 10 messages. But it would not remeber the 12 th message. So it forgets about what we discussed before.

#### If each turn adds ~100-200 tokens, how many turns can fit in a 4096-token context window?

Between 20 and 40 turns can fit in that context windows.