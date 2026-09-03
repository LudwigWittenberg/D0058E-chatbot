# Rapport Lab 1 - Chatbot

## Table of contents
- [Task 1.1](#task-11)
- [Task 1.2](#task-12)
- [Task 1.3](#task-13)
- [Task 1.4](#task-14)

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