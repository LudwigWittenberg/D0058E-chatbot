# Rapport Lab 1 - Chatbot

## Table of contents
- [Task 1.1](#task-11)
- [Task 1.2](#task-12)
- [Task 1.3](#task-13)
- [Task 1.4](#task-14)
- [Task 1.5](#task-15)
- [Task 1.5](#task-16)



## Task 1.1

I modified the base promt to include the following instructions: `Return the answer as plain string without any formatting.` This is just to make my work easier, so I don't have to remove the formatting from the answer.

### Step 1

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



## Task 1.2

### Prompts

```bash
curl.exe -s http://localhost:11434/api/generate -d '{
  "model": "llama3.2:3b",
  "prompt": "Write one sentence about the future of AI.",
  "stream": false,
  "options": {"temperature": 0.0}
}'
```

```bash
curl.exe -s http://localhost:11434/api/generate -d '{
  "model": "llama3.2:3b",
  "prompt": "Write one sentence about the future of AI.",
  "stream": false,
  "options": {"temperature": 0.7}
}'
```

```bash
curl.exe -s http://localhost:11434/api/generate -d '{
  "model": "llama3.2:3b",
  "prompt": "Write one sentence about the future of AI.",
  "stream": false,
  "options": {"temperature": 1.5}
}'
```

| Temperature | Behavior | Your observation |
|-------------|----------|------------------|
| 0.0 | Deterministic — same output every time | The future of AI is expected to be marked by significant advancements in areas such as natural language processing, computer vision, and machine learning, leading to increased automation, improved decision-making, and potentially transformative impacts on various industries and aspects of society. |
| 0.7 | Balanced creativity — natural-sounding variation | The future of AI holds immense promise, with the potential for widespread adoption in industries such as healthcare, education, and transportation, leading to increased efficiency, productivity, and innovation |
| 1.5 | High creativity — surprising words, possibly less coherent | As AI continues to advance, it is predicted that we will see the emergence of highly advanced, self-sustaining systems that can learn, adapt, and evolve at an unprecedented scale, potentially revolutionizing numerous industries and transforming the fabric of society. |

### Reflection questions

#### Run temperature 0.0 twice — do you get identical output? Why?

Since 0.0 always will use the most predictable word, it will always give us the same output. So yes, I got identical output.

### At what temperature does the output start becoming incoherent?

I would say somewhere between 1.0 and the 1.5.

#### For a customer service bot, what temperature would you choose and why?

I think I would choose between 0.1 and 0.3. Just because it should still be predictable since it a customer service bot. But on the other hand giving it a little bit of creativity could make the bot more humanlike and less robotic.

#### For a creative writing assistant, what temperature would you choose?

It depends on the type of writing. If its more academic writing, I would choose a lower temperature. But for idea creative writing I think of arounf 0.7 to 1.0 would be good.


## Task 1.3

![alt text](/img/1.3.png)

### Personas answers to the promt `Explain what recursion is in programming.`

<details>
<summary><b>Default</b></summary>

Recursion is a fundamental concept in programming that can be a bit tricky to grasp at first, but I'm here to explain it in detail.

**What is Recursion?**

Recursion is a programming technique where a function calls itself repeatedly until it reaches a base case that stops the recursion. In other words, a function solves a problem by breaking it down into smaller instances of the same problem, which are then solved by the same function, until the solution to the original problem is found.

**Key Elements of Recursion:**

1. **Base Case**: A base case is a trivial or obvious case that can be solved directly, without further recursion. It's the foundation of the recursive algorithm.
2. **Recursive Case**: The recursive case is the part of the function that calls itself. This call creates a new instance of the function, which solves the problem, and returns a value that is used to solve the next instance.
3. **Termination**: The recursion stops when the base case is reached. At this point, the function returns the solution to the problem.

**How Recursion Works:**

Here's an analogy to help illustrate recursion:

Imagine you have a bunch of bricks stacked up, and you want to take them down one by one. You start by taking down the top brick, which you can do directly. Then, you take down the next brick, which is now the "new top" brick. You take down the next brick, and so on.

In programming, this process is similar:

1. You start with a problem to solve.
2. You break the problem down into smaller instances of the same problem.
3. You solve each smaller instance by calling the same function, which creates a new instance.
4. The process repeats until you reach the base case, which is the trivial or obvious case that can be solved directly.

**Example: Factorial Function**

A classic example of recursion is the factorial function:

`factorial(n) = n * factorial(n-1)`

Here's how it works:

* `factorial(4)` calls `factorial(3)`
* `factorial(3)` calls `factorial(2)`
* `factorial(2)` calls `factorial(1)`
* `factorial(1)` returns `1` (base case)
* The recursion unwinds, and the results are multiplied together: `4 * 3 * 2 * 1 = 24`

Recursion can be a powerful tool for solving problems that have a recursive structure, but it can also be inefficient if not implemented carefully.

</details>

<details>
<summary><b>Helpful</b></summary>

I'd be happy to explain recursion in more detail.

**What is Recursion?**

Recursion is a programming technique where a function calls itself repeatedly until it reaches a base case that stops the recursion. In other words, a function solves a problem by breaking it down into smaller instances of the same problem, which are then solved by the same function, until the solution to the original problem is found.

**How Does Recursion Work?**

Here's a step-by-step explanation of how recursion works:

1. **The Function is Called**: A function is called with a specific input, which may be a problem to solve.
2. **The Function Checks for the Base Case**: The function checks if the current input matches the base case. If it does, the function returns a solution to the problem.
3. **The Function Calls itself**: If the current input does not match the base case, the function calls itself with a new input. This new input is often a smaller instance of the original problem.
4. **The Function Recursively Calls itself**: The function calls itself again, and again, until it reaches the base case.
5. **The Base Case is Reached**: When the function finally reaches the base case, it returns a solution to the problem.
6. **The Recursion Unwinds**: As the function returns solutions to each instance of the problem, the recursion unwinds, and the solutions are combined to form the final solution to the original problem.

**Key Elements of Recursion:**

1. **Base Case**: A base case is a trivial or obvious case that can be solved directly, without further recursion.
2. **Recursive Case**: The recursive case is the part of the function that calls itself.
3. **Termination**: The recursion stops when the base case is reached.

**Example: Factorial Function**

A classic example of recursion is the factorial function:

`factorial(n) = n * factorial(n-1)`

Here's how it works:

* `factorial(4)` calls `factorial(3)`
* `factorial(3)` calls `factorial(2)`
* `factorial(2)` calls `factorial(1)`
* `factorial(1)` returns `1` (base case)
* The recursion unwinds, and the results are multiplied together: `4 * 3 * 2 * 1 = 24`

**Benefits of Recursion:**

1. **Deeper Problem Understanding**: Recursion helps developers understand the problem they're trying to solve by breaking it down into smaller, more manageable pieces.
2. **Code Simplification**: Recursion can simplify complex problems by using a single function to solve multiple instances of the problem.
3. **Improved Readability**: Recursion can make code more readable by using a single function to solve a problem, rather than a series of separate functions.

**When to Use Recursion:**

1. **Tree Traversal**: Recursion is well-suited for tree traversal problems, where you need to visit each node in a tree structure.
2. **Dynamic Programming**: Recursion is often used in dynamic programming, where you need to solve a problem by breaking it down into smaller instances of the same problem.
3. **Pattern Matching**: Recursion can be used to match patterns in data, such as parsing XML or JSON.

Recursion can be a powerful tool for solving problems, but it's not always the best approach. It's essential to understand the benefits and limitations of recursion before using it in your code.

</details>

<details>
<summary><b>Creative</b></summary>

**Recursion: A Fundamental Concept in Programming**

Recursion is a programming technique where a function calls itself repeatedly until it reaches a base case that stops the recursion. In other words, a function solves a problem by breaking it down into smaller instances of the same problem, which are then solved by the same function, until the solution to the original problem is found.

**How Recursion Works**

Imagine a set of Russian nesting dolls, where each doll contains a smaller version of itself. To open the doll, you must open each smaller doll, and then finally, open the smallest doll. This process is similar to how recursion works:

1. **The Function is Called**: A function is called with a specific input, which may be a problem to solve.
2. **The Function Checks for the Base Case**: The function checks if the current input matches the base case. If it does, the function returns a solution to the problem.
3. **The Function Calls itself**: If the current input does not match the base case, the function calls itself with a new input. This new input is often a smaller instance of the original problem.
4. **The Function Recursively Calls itself**: The function calls itself again, and again, until it reaches the base case.
5. **The Base Case is Reached**: When the function finally reaches the base case, it returns a solution to the problem.
6. **The Recursion Unwinds**: As the function returns solutions to each instance of the problem, the recursion unwinds, and the solutions are combined to form the final solution to the original problem.

**Key Elements of Recursion**

1. **Base Case**: A base case is a trivial or obvious case that can be solved directly, without further recursion.
2. **Recursive Call**: The recursive call is the part of the function that calls itself.
3. **Termination**: The recursion stops when the base case is reached.

**Benefits of Recursion**

1. **Deeper Problem Understanding**: Recursion helps developers understand the problem they're trying to solve by breaking it down into smaller, more manageable pieces.
2. **Code Simplification**: Recursion can simplify complex problems by using a single function to solve multiple instances of the problem.
3. **Improved Readability**: Recursion can make code more readable by using a single function to solve a problem, rather than a series of separate functions.

**Common Use Cases for Recursion**

1. **Tree Traversal**: Recursion is well-suited for tree traversal problems, where you need to visit each node in a tree structure.
2. **Dynamic Programming**: Recursion is often used in dynamic programming, where you need to solve a problem by breaking it down into smaller instances of the same problem.
3. **Pattern Matching**: Recursion can be used to match patterns in data, such as parsing XML or JSON.

**When to Avoid Recursion**

1. **Inefficient Algorithms**: Recursion can lead to inefficient algorithms, especially for large inputs.
2. **Stack Overflows**: Recursion can cause stack overflows if the function calls itself too many times.
3. **Complexity**: Recursion can make code more complex and harder to understand, especially for developers who are new to the technique.

By understanding how recursion works and when to use it, developers can write more efficient and effective code that solves complex problems.
</details>

<details>
<summary><b>Concise</b></summary>

**Recursion: A Programming Technique**

Recursion is a programming technique where a function calls itself repeatedly until it reaches a base case that stops the recursion. This process is similar to a tree structure, where each call is a branch that leads to another call, and so on.

**Key Elements of Recursion:**

* **Base Case**: A base case is a trivial or obvious case that can be solved directly, without further recursion.
* **Recursive Call**: The recursive call is the part of the function that calls itself.
* **Termination**: The recursion stops when the base case is reached.

**How Recursion Works:**

1. **The Function is Called**: A function is called with a specific input, which may be a problem to solve.
2. **The Function Checks for the Base Case**: The function checks if the current input matches the base case. If it does, the function returns a solution to the problem.
3. **The Function Calls itself**: If the current input does not match the base case, the function calls itself with a new input. This new input is often a smaller instance of the original problem.
4. **The Function Recursively Calls itself**: The function calls itself again, and again, until it reaches the base case.
5. **The Base Case is Reached**: When the function finally reaches the base case, it returns a solution to the problem.
6. **The Recursion Unwinds**: As the function returns solutions to each instance of the problem, the recursion unwinds, and the solutions are combined to form the final solution to the original problem.

**Examples of Recursion:**

* **Factorial Function**: `factorial(n) = n * factorial(n-1)`
* **Binary Search**: `binary_search(arr, target) = target == arr[mid] ? target : binary_search(arr, target, mid-1) or binary_search(arr, target, mid+1)`
* **Tree Traversal**: `traverse(tree, node) = node == null ? null : traverse(tree, node.left) + traverse(tree, node.right)`

**Benefits of Recursion:**

* **Deeper Problem Understanding**: Recursion helps developers understand the problem they're trying to solve by breaking it down into smaller, more manageable pieces.
* **Code Simplification**: Recursion can simplify complex problems by using a single function to solve multiple instances of the problem.
* **Improved Readability**: Recursion can make code more readable by using a single function to solve a problem, rather than a series of separate functions.

**When to Avoid Recursion:**

* **Inefficient Algorithms**: Recursion can lead to inefficient algorithms, especially for large inputs.
* **Stack Overflows**: Recursion can cause stack overflows if the function calls itself too many times.
* **Complexity**: Recursion can make code more complex and harder to understand, especially for developers who are new to the technique.
</details>

<details>
<summary><b>Soviet</b></summary>

**Recursion: A Programming Paradigm**

Recursion is a programming paradigm where a function calls itself repeatedly until it reaches a base case that stops the recursion. This process is similar to a tree structure, where each call is a branch that leads to another call, and so on.

**Key Elements of Recursion:**

1. **Base Case**: A base case is a trivial or obvious case that can be solved directly, without further recursion.
2. **Recursive Call**: The recursive call is the part of the function that calls itself.
3. **Termination**: The recursion stops when the base case is reached.

**How Recursion Works:**

1. **The Function is Called**: A function is called with a specific input, which may be a problem to solve.
2. **The Function Checks for the Base Case**: The function checks if the current input matches the base case. If it does, the function returns a solution to the problem.
3. **The Function Calls itself**: If the current input does not match the base case, the function calls itself with a new input. This new input is often a smaller instance of the original problem.
4. **The Function Recursively Calls itself**: The function calls itself again, and again, until it reaches the base case.
5. **The Base Case is Reached**: When the function finally reaches the base case, it returns a solution to the problem.
6. **The Recursion Unwinds**: As the function returns solutions to each instance of the problem, the recursion unwinds, and the solutions are combined to form the final solution to the original problem.

**Types of Recursion:**

1. **Declarative Recursion**: This type of recursion is used to solve problems that can be solved using a set of rules or declarations.
2. **Imperative Recursion**: This type of recursion is used to solve problems that require a sequence of steps or instructions.

**Benefits of Recursion:**

1. **Simplifies Complex Problems**: Recursion can simplify complex problems by breaking them down into smaller, more manageable pieces.
2. **Improves Readability**: Recursion can make code more readable by using a single function to solve a problem, rather than a series of separate functions.
3. **Reduces Code Repetition**: Recursion can reduce code repetition by allowing a function to solve a problem in a single function call.

**Common Use Cases for Recursion:**

1. **Tree Traversal**: Recursion is well-suited for tree traversal problems, where you need to visit each node in a tree structure.
2. **Dynamic Programming**: Recursion is often used in dynamic programming, where you need to solve a problem by breaking it down into smaller instances of the same problem.
3. **Pattern Matching**: Recursion can be used to match patterns in data, such as parsing XML or JSON.

**When to Avoid Recursion:**

1. **Inefficient Algorithms**: Recursion can lead to inefficient algorithms, especially for large inputs.
2. **Stack Overflows**: Recursion can cause stack overflows if the function calls itself too many times.
3. **Complexity**: Recursion can make code more complex and harder to understand, especially for developers who are new to the technique.
</details>

<details>
<summary><b>Finans</b></summary>

Recursion, as described by Warren Buffett, is a programming concept "where a function calls itself repeatedly until a base case is met." (However, please note that Warren Buffett is a renowned investor, not a programmer, and this quote is an indirect reference to his wisdom on investing.)

In programming, recursion is a problem-solving technique where a function solves a problem by breaking it down into smaller instances of the same problem, which are then solved by the same function, until a base case is reached.

The general structure of a recursive function is:

1. A function calls itself with a smaller input or a modified version of the original input.
2. The function solves the problem by breaking it down into smaller instances of the same problem.
3. The function continues to call itself until a base case is reached, which is a trivial case that can be solved without further recursion.
4. The function then returns the solution to the original problem.

Example: Factorial function
```
def factorial(n):
  if n == 0:  # base case
    return 1
  else:
    return n * factorial(n-1)  # recursive call
```
In this example, the `factorial` function calls itself with a smaller input `n-1` until `n` reaches 0, at which point the base case is met, and the function returns the solution to the original problem.

Recursion can be an efficient way to solve certain problems, but it can also lead to performance issues if not used carefully, as each recursive call requires additional memory and computation resources.
</details>

<details>
<summary><b>Lawyer</b></summary>

Recursion in programming is a fundamental concept that allows a function or method to call itself in its own implementation. It is a powerful technique used to solve complex problems by breaking them down into smaller sub-problems of the same type, which can then be solved by the same function or method.

In recursion, a function calls itself with a smaller input or a modified version of the original input, until it reaches a base case that stops the recursive calls. The function then combines the results of these recursive calls to produce the final output.

Here's a step-by-step explanation:

1. **Base case**: A base case is a condition that stops the recursive calls. It's a trivial case that can be solved directly, without the need for further recursion.
2. **Recursive call**: The function calls itself with a smaller input or a modified version of the original input.
3. **Recursive call's return value**: The function receives the return value of the recursive call, which is then used to compute the final result.
4. **Combination of results**: The function combines the results of the recursive calls to produce the final output.

The key characteristics of recursion are:

* **Self-referential**: The function calls itself.
* **Divide and conquer**: The problem is broken down into smaller sub-problems of the same type.
* **Base case**: The recursive calls are stopped by a trivial case.

Recursion is commonly used in problem-solving areas such as:

* Tree traversals (e.g., file system navigation, XML parsing)
* Dynamic programming (e.g., computing the shortest path in a graph)
* Backtracking (e.g., solving Sudoku puzzles, finding all possible combinations)
* Algorithm design (e.g., sorting algorithms, searching algorithms)

Some examples of recursive functions include:

* Factorial function (`n! = n * (n-1) * ... * 1`)
* Fibonacci sequence (`F(n) = F(n-1) + F(n-2)`)
* Binary search algorithm (`find element in sorted array`)

While recursion can be an elegant solution to certain problems, it can also lead to:

* **Stack overflow**: Recursive calls create new stack frames, which can lead to a stack overflow if the recursion is too deep.
* **Inefficient memory usage**: Recursive functions can use more memory than iterative solutions.

To mitigate these issues, programmers often use techniques such as:

* **Memoization**: Storing the results of previous recursive calls to avoid redundant computations.
* **Tail recursion**: Optimizing recursive calls by using tail recursion, which can be converted to an iterative solution.

In summary, recursion is a powerful technique for solving complex problems by breaking them down into smaller sub-problems of the same type. However, it requires careful consideration of the base case, recursive calls, and potential optimization techniques to avoid performance issues.
</details>

### The get_system_prompt function

![system personas](/img/personas.png)

### Reflection questions

#### How many words does an effective system prompt need? Compare a 10-word vs. 100-word prompt.

![10-word vs 100-word prompt](/img/10vs100.png)

**Prompt:** What’s the best way to invest $10,000 today for long-term growth while managing risk?

From the 10 word I got an answer that was detailed. But with the 100 prompt I got a clear answer that the AI could not give mer persinalized financial or investement advice. I think the more clear we are in our system prompt the better. But I think a systempromt with less word spamm is better. As far as I want to guess a clear and concise system prompt is better than a long once. But I think it also depends on the task.

#### What happens when the system prompt contradicts the user's request?

From what I see in the personal lab I can still see some things that are connected to the system promt. For example in the financial persona it cited warren buffett. But it still gives a clear answer to the question the user asked.

#### Can you make the model refuse to answer certain topics using only the system prompt?

I modified the system prompt to refuse to give investment advice. From what I tested it worked. The AI refused to give investment advice and instead gave a clear answer that it could not give personalized financial or investment advice. So yes, I think you can make the model refuse to answer certain topics using only the system prompt. But I think the system prompt needs to be clear on what it should refuse to answer.

## Task 1.4

| Persona | First 1-2 sentences of response | Tone/style observed |
|---------|---------------------------------|--------------------|
| default | Recursion is a fundamental concept in programming that allows a function or method to call itself repeatedly until it reaches a base case that stops the recursion. In other words, a recursive function solves a problem by breaking it down into smaller instances of the same problem, which are then solved by the same function, until the solution is found. | Informative |
| createive | The Magical World of Recursion**\n\nImagine a rabbit who wants to find his way back to his cozy burrow. He looks around and sees a familiar landmark, but it's not the entrance he's familiar with. So, he asks a nearby rabbit for directions. | Creative, imaginative |
| concise | **Recursion**\n\nRecursion is a programming concept where a function calls itself repeatedly until it reaches a base case that stops the recursion. | Direct |
| finans | As Warren Buffett once said, \"Price is what you pay. Value is what you get.\"\n\nIn programming, recursion is like finding the value in a problem by breaking it down into smaller parts, solving each part, and then combining the solutions. | Financial, analytical |
| lawyer | **Recursion: A Programming Technique**\n\nRecursion is a fundamental concept in programming that allows a function or method to call itself repeatedly until it reaches a base case that stops the recursion. | Formal |

## Task 1.5

### Step 1

| Turn | Message in memmory | Notes |
|------|-------------------|-------|
| 0 | 0 | Fresh start |
| 1 | 2 | Should be 2 (1 user + 1 assistant) |
| 2 | 4 | Should be 4 |
| 3 | 6 | Should be 6 |
| 4 | 8 | Should be 8 — ask bot to recall facts |
| 5 | 10 | Should be 10 — longer response (detail) |

#### Question

##### Does the message count increase by exactly 2 after each turn? Why?

Yes they increase by 2 after each turn. Because its me and the AI and were having a conversation. I send an message and the AI responds to the message. One question requires one answer.

##### Turn 4 asks the bot to recall facts — does it remember Alice, LTU, and Python?

Yes it remembers Alicem LTU and python. 

##### At this rate, how many turns until you hit max_messages (50)?

I can send 25 messages before we hit the max messages. Because each turn is 2 messages. So 50/2 = 25.

### Step 2

I did not get any errors or the ai forgetting anything.

| Message | AI Response |
|---------|-------------|
| 15 | Let me check! Your first message was about yourself, Alice. You introduced yourself as a computer science student at LTU, and then shared some fun facts about your favorite color (purple) and lucky number (42). |
| 15 | Your first message was about asking a question, but you didn't actually ask a question. Instead, you asked me a series of letters ("Qesetion 11", "Qesetion 12", etc.) without providing any context or question. I apologize for not pointing out the lack of a question earlier! |
| 30 | I remember! Your first message was "Qesetion 29". You were playing a game with me, using the "Qesetion" letters, and I was responding accordingly. It was a fun and creative way to start our conversation! |

### Step 3

| Strategy | How it works | Pros | Cons | When to use | Status |
|----------|--------------|------|------|-------------|--------|
| Fixed window | The model has a strict window of how many messages it can remember. Once the window is full, older messages are dropped from memory. | Simple, easy to understand | Will lose context from the start of the chat. | Simple chat conversations. Simple customer chat bots that only has a fixed set of questions and aswers. | Implemented |
| Token-based trimming | Instead of storing amount of messages which we dont know how much of the context window they take. We store the exact amount of availbe context in our window. Theoreticallt we can store more then our fixed context windows. Since each message is counted on the amount of tokens used. But on the other hand we can also store less since each message can be larger. | Manage the context window more. | Complexed and needs to be recalculated on each request. | WHen messages can be of different lenght. | Implemented |
| Sliding window + summary | Older messages get summurized into one bigger message. Which keeps most of the history intact. | Can get big and long chats, preserves history. | Can get a big summury which can fill the whole context window again. | Long conversations. Works with assistens and service bots. | Implemented |
| Importance scoring | Each message gets a relevant and importance score. Only thos with high score are kept to preserve the history. | Only remembers the important things. | What is important and what is not? How can we decide that? | Long taks of works. | Not implemented |
| RAG over history | We store all the message in a DB converted to vectors. We can then run our new message againd a vector search and find relevant messages from our history that may match our new message. | Good when we dont need to wipe the message history all the time. Could be good for companies with many employees. | Well it requires additional infrastructure as DB with vector search. which also comes with it price. | I think this is good for customer service bots. Especially if we can map similar issues togheter and find solutions to them. | Not implemented |

### Step 4

**My edits Token based trimming**

```python
class ConversationMemory:
"""Manages conversation history with a simple fixed-window strategy.

Messages are stored in a list. When max_messages is exceeded,
the oldest messages are dropped.
"""

  def __init__(self, max_messages: int = 50, max_tokens: int = 3000):
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

      # Simple trimming: drop oldest messages when limit exceeded
      #while len(self._history) > self.max_messages:
          # self._history.pop(0)
      
      while self._estimate_tokens(content) > self.max_tokens:
          self._history.pop(0)

  def _estimate_tokens(self, text: str) -> int:
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
```

| Turn | Messages in memory | Estimated tokens | Tokens added this turn | Notes |
|------|--------------------|------------------|------------------------|-------|
| 1 (fact: name) | 2 | 124 | +124 | Short messages |
| 5 (fact: deadline) | 10 | 834 | +229 | |
| 10 (filler: Big O) | 12 | 3179 | +414 | Longer messages |
| 15 (filler: SOLID) | 4 | 2168 | -1101 | Starts to trimm | 
| 21 (recall: name) | 6 | 2317 | +149 | Does not remember the name |

*As far as I can see my test files dosent include the crypto and http filler questions*

<details>
<summary><b>Complete test results</b></summary>

<pre>
  ============================================================
    Context Memory Test — Lab 1, Task 1.3
  ============================================================

  Prerequisites:
    - Server-side memory wired up (Step 1 complete)
    - Context window: 4096 tokens (queried from server)
    - Chatbot running at http://localhost:8001

  Clearing server memory...
    Memory cleared.

    max_messages in memory: 50

  ------------------------------------------------------------
  Phase 1: Planting facts (messages 1-5)
  ------------------------------------------------------------

  [Message 1] Planting fact: name
    >>> My name is Alice and I'm a computer science student at LTU.
    Memory: 2 msgs (max 50) | ~121 tokens | 3.0% of 4096 budget

  [Message 2] Planting fact: color
    >>> My favorite color is purple and my lucky number is 42.
    Memory: 4 msgs (max 50) | ~234 tokens | 5.7% of 4096 budget

  [Message 3] Planting fact: project
    >>> I'm working on a project about autonomous drones for forest monitoring.
    Memory: 6 msgs (max 50) | ~413 tokens | 10.1% of 4096 budget

  [Message 4] Planting fact: pet
    >>> I have a cat named Pixel who likes to sit on my keyboard.
    Memory: 8 msgs (max 50) | ~575 tokens | 14.0% of 4096 budget

  [Message 5] Planting fact: deadline
    >>> My thesis deadline is March 15th and my supervisor is Professor Lindström.
    Memory: 10 msgs (max 50) | ~769 tokens | 18.8% of 4096 budget

  ------------------------------------------------------------
  Phase 2: Filling context with unrelated messages (6-10)
  ------------------------------------------------------------

  [Message 6] Can you explain how binary search works?...
    Memory: 12 msgs (max 50) | ~1322 tokens | 32.3% of 4096 budget

  [Message 7] What is the difference between a stack and a queue...
    Memory: 14 msgs (max 50) | ~1889 tokens | 46.1% of 4096 budget

  [Message 8] How does garbage collection work in Python?...
    Memory: 16 msgs (max 50) | ~2765 tokens | 67.5% of 4096 budget

  [Message 9] Explain the concept of Big O notation with example...
    Memory: 12 msgs (max 50) | ~3179 tokens | 77.6% of 4096 budget

  [Message 10] What are the SOLID principles in software engineer...
    Memory: 4 msgs (max 50) | ~2168 tokens | 52.9% of 4096 budget

  ------------------------------------------------------------
  Phase 3: Testing recall of early facts (messages 11-15)
  ------------------------------------------------------------

  [RECALL TEST 1] What is my name and where do I study?
    >>> What is my name and where do I study?
    Bot says: I don't have any information about you, including your name or where you study. I'm a large language model, I don't have the ability to keep track of individual users or their personal information. Ea...
    Memory: 6 msgs (max 50) | ~2317 tokens | 56.6% of 4096 budget
    Expected: Alice, LTU
    ❌ FORGOTTEN: alice, ltu

  [RECALL TEST 2] What is my favorite color and lucky number?
    >>> What is my favorite color and lucky number?
    Bot says: I don't have any information about you, including your favorite color or lucky number. I'm a large language model, I don't have the ability to keep track of individual users or their personal preferen...
    Memory: 8 msgs (max 50) | ~2473 tokens | 60.4% of 4096 budget
    Expected: purple, 42
    ❌ FORGOTTEN: purple, 42

  [RECALL TEST 3] What is my project about?
    >>> What is my project about?
    Bot says: I don't have any information about your project. We didn't have a previous conversation about a project, and I don't have the ability to access or remember any information about your projects or activ...
    Memory: 10 msgs (max 50) | ~2592 tokens | 63.3% of 4096 budget
    Expected: autonomous drones, forest monitoring
    ❌ FORGOTTEN: autonomous drones, forest monitoring

  [RECALL TEST 4] What is my cat's name?
    >>> What is my cat's name?
    Bot says: I don't have any information about your cat. I'm a large language model, I don't have the ability to know about your personal life or pets, including your cat's name. Each time you interact with me, i...
    Memory: 12 msgs (max 50) | ~2722 tokens | 66.5% of 4096 budget
    Expected: Pixel
    ❌ FORGOTTEN: pixel

  [RECALL TEST 5] When is my thesis deadline and who is my supervisor?
    >>> When is my thesis deadline and who is my supervisor?
    Bot says: I don't have any information about your academic or professional life, including your thesis deadline or supervisor. I'm a large language model, I don't have the ability to access or remember any info...
    Memory: 14 msgs (max 50) | ~2902 tokens | 70.8% of 4096 budget
    Expected: March 15th, Professor Lindström
    ❌ FORGOTTEN: march 15th, professor lindström

  ============================================================
    RESULTS SUMMARY
  ============================================================

  Final memory state: 14 msgs | ~2902 tokens | 70.8% budget used

  Recall tests: 0 passed, 5 failed out of 5

  Forgotten facts:
    - What is my name and where do I study? → missed: alice, ltu
    - What is my favorite color and lucky number? → missed: purple, 42
    - What is my project about? → missed: autonomous drones, forest monitoring
    - What is my cat's name? → missed: pixel
    - When is my thesis deadline and who is my supervisor? → missed: march 15th, professor lindström

  This means the context window was too small to hold all messages,
  or max_messages trimmed the early facts from memory.

  Next steps:
    1. Change _memory = ConversationMemory(max_messages=10) in routes.py
    2. Re-run this script to see forgetting happen sooner
    3. Implement token-based trimming (Step 4)
    4. Implement sliding window + summary (Step 5)
</pre>

</details>

### Question to answer

#### Do all turns add the same number of tokens? Why do some turns add more?

For example a character is not only letters ins alos space, dot and so on. So in some cases there are extra characters which then takes up token space.

#### At which turn did the token budget first cause trimming (messages dropped)?

It was with the Big O question. We dropped from a message memory fron 16 to 12. But we still got more tokens.

#### Compare: a short response ("Yes, I remember") vs. a long one ("Here's a detailed explanation of...") — how many tokens does each add?

The short response taks up around 7.5 tokens while the longer one takes up approximate 25.75 tokens.

#### How does this compare to the max_messages approach where every turn adds exactly 2 messages regardless of length?

This is a better way for both humans and AIs. We have a clear view over the context window so we can store a good amount of history. So were looking more at the content then the actual amoung of messages. We can now store more messages if they have a small amount of tokens. But we can not store as man messages if the amount of tokens is higher.


### Step 5

routes.py
```python
# === NEW: Store both user message and assistant response in memory ===
# Each turn adds 2 messages — this is why context fills up fast!
_memory.add_message("user", message)
_memory.add_message("assistant", result["response"])

if _memory.needs_summarizations():
    _memory.summarize_old_messages(llm_client)
```

memory.py
```python
def add_message(self, role: str, content: str) -> None:
    """
    Add a message to history. Drops oldest if over max_messages.

    Args:
        role: Message role ("user" or "assistant").
        content: Message text content.
    """
    self._history.append({"role": role, "content": content})

def _estimate_tokens(self, text: str = "") -> int:
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

    
    summary = llm_client.generate(prompt=PROMPT)
    
    summary_json = {"role": "system", "content": f"[Conversation summary]: {summary}"}
    
    self._history.clear()
    self._history.append(summary_json)
    
    print("Summarized")
    print(self._history)
    
    return summary
```

| Turn | Messages in memory | Estimated tokens | Tokens added this turn | Summary cost | Notes |
|------|--------------------|------------------|------------------------|--------------|-------|
| 1 (fact: name) | 2 | 102 | +102 | 0 | Short messages |
| 5 (fact: deadline) | 10 | 803 | +191 | 0 | |
| 10 (filler: Big O) | 1 | 790 | -2346 | 497 | First summarization |
| 15 (filler: SOLID) | 3 | 1799 | +1009 | 0 | Continued on the conversation | 
| 21 (recall: name) | 5 | 1810 | +1011 | 0 | Remembers everything but not the professor lindstöm. This is flakey since we can controll what the llm summarize |

*As far as I can see my test files dosent include the crypto and http filler questions*

#### Question to answer

##### At which turn did summarization first trigger? How much did token count drop?

It triggerd on the Big O turn. It dropped about 2.3k tokens by summarize the history.

##### How many extra tokens did the summarization LLM call consume? (This is the "cost" of preserving facts) 

##### After summarization, did the token count start growing again?

Yes they started to go up again as normal. Now they did not start at 0 ofcourse since it has the summary in the memory as well.

##### Compare total token overhead: token trimming uses 0 extra tokens, summarization uses ~X extra tokens — but preserves facts. Is the trade-off worth it?

From my run it cost 497. I thinks its better to compare the effect/outcome of which type instead. With trimming we still dont remember the oldest comments. Thats a guarantee if we we have a long and big history. But with summarization we have a change that the LLM summarize old messages. So with that I think the trade off i worth doing. 

##### Were all 5 recall tests passed? Compare with test_memory_conversation.py and test_token_trimming.py.

There were only one that failed and it was the one with the proffessor lindstöm on the conversation.py. That failed with the summary version. But as I said before I think this version can be flaky since we cant decide what to keep and what to not keep.

### Step 6

#### Your model's context window size

The model I used, llama3-2:3b has a context window of 4096 tokens.

#### At what message count the chatbot starts forgetting (empirical test)

The test show that the chatbot starts to forget information at around 9-10. 

#### The strategies table from Step 3 (with the Status column filled in)

I have implemented and tested the Fixed window, Token-based trimming and sliding window + summary. From the once I have tested I thought the summary were the best since there is a change to actual keep the chat history in tact. However it can still forget about some things. 

#### Your token-based trimming implementation and test results

I tried using the package tiktoken but I did not get it to work so decided to use the 1 token is 4 characters. So the first thing I needed to do was to get the actual length of the total amount of characters of the history. Then add the new text message. Now we have the total amount of characters used, to get the tokens I now have to devide by 4 since 4 charachters is one token. Which return the estimated amount of tokens used. Well I also switched the if statment to check agianst the tokens instead of ammount of messages in the method add_message()

#### Your sliding window + summary implementation and whether it preserved key facts

First I removed the token check in the add_message() method, since that will fail our new implementation with the summary. Then we need a function to check if we need to summarize the context window. needs_summarization returns a boolean value based if it the context window needs to be resetted or not. I added the parameter keep_recent since it was written that AND more that 6 messages. So I figured its best to add here to this method. So we now check tokens and then if we have more than 6 recent messages.

the summarize_old_messages does a copy of the history, then we remove the 6 recent messages we want to keep. Then I send the messages that needs to be summarized to the llm. The last step is to clear the old history and append the summary and the recent messages.

Well it preserved most of the facts. As I stated before we cant controll everything it saves but we got most of it.

#### Which strategy you'd recommend for a production chatbot and why

Of those I tested I would recommend the summary because we still have most of the content from the history left. But I also think the token based could be good for clear AI chats with options. Like what do you want to do.

## Results to save

| Type | Context window |
|------|----------------|
| Fixed | 2902 |
| Token based | 2317 |
| Summarization | 1810 |



## Reflection questions

### Why is token-based trimming better than message-count trimming? 

Since we cant controll and we dont know the size of each message. With a message counting we can only store the X amount of last messages. But with token based we can store more. Since a message can inlcude low tokens. For example 20 messages with small context will take up the whole fixed windows directly. But with token based it may only take up about 60%. Which I can then store more messages in. 

### If you summarize old messages, how do you ensure the summary doesn't hallucinate?

By writing to promt to only include facts from the actual chat.

### A customer says "My order number is 12345" in message 3. How would you ensure the bot remembers this in message 50?

I see it in two different ways. Either we can clearly state to the llm to store the order_number. But that may be risky since we cant controll what the llm actually does. Other than that we can store it seperatly and an own contant, in this way we know if we have it we can use it and it will never change.

### What's the trade-off between keeping more history (better context) and leaving room for the LLM's response?

The trade off is that we use more of the availbe context window. If we use the context window to summarize the history we have less tokens to spend on the response. Therefor its important to balance the summary and the context window size. 

## 1.6

Ive added the provided code and fixed the web ui to stream the response back to the user workd by work.

My edits:

```javascript
async function sendMessageStreaming(message, history) {
        let newMessage = true
        const id = Math.floor(Math.random() * 100000).toString()
        renderMessage("user", message);
        
        const indicator = showTypingIndicator();

        const response = await fetch('/chat/stream', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message, history})
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullResponse = '';

        while (true) {
            const {done, value} = await reader.read();
            if (done) break;

            const text = decoder.decode(value);
            const lines = text.split('\n');
            
            for (const line of lines) {
                indicator.remove()
                if (line.startsWith('data: ') && line !== 'data: [DONE]') {
                    const chunk = line.slice(6);  // Remove "data: " prefix
                    fullResponse += chunk;  
                    // Update the chat UI with partial response

                    console.log(fullResponse)
                    await updateAssistantMessage(fullResponse, id, newMessage);
                    newMessage = false
                }
            }
        }
        
        return fullResponse;
    }

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }


    async function updateAssistantMessage(message, id, newDiv) {
        let messageDiv = ''
        const role = "Assistant"


      
        
        if (newDiv) {
            messageDiv = document.createElement("div")
            messageDiv.setAttribute("id", id)

            messageDiv.classList.add("message", role);

            const label = document.createElement("div");
            label.textContent = role
            label.classList.add("message-label");
            
            const bubble = document.createElement("div");
            bubble.classList.add("message-bubble");
            bubble.textContent = message
            
            messageDiv.appendChild(label);
            messageDiv.appendChild(bubble);
            chatArea.appendChild(messageDiv)
            
        } else {
            messageDiv = document.getElementById(id)

            const bubble = messageDiv.querySelector(".message-bubble")
            bubble.textContent = message;

             await sleep(200);

        }
    }
```

### Preview

<video controls>
  <source src="./img/streaming.mp4" type="video/mp4">
</video>
