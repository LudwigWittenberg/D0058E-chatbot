"""Custom tool definitions for the agents app.

Tools extend agent capabilities beyond pure text generation.
In Task 3.5, you will implement custom tools here.

A tool needs:
- name: identifier for registration
- description: tells the agent when/how to use it (the agent reads this!)
- run(input: str) -> str: executes logic and returns text result

For now, this file is empty — the default crew runs without tools.
Students add tools in Task 3.5.
"""

# TODO (Task 3.5): Implement custom tools here
# See the 🔧 Tools & MCP tab for instructions and examples
#
# Example structure:
#
# from crewai.tools import BaseTool
#
# class WordCountTool(BaseTool):
#     name: str = "word_counter"
#     description: str = "Count words in text. Input: text to analyze."
#
#     def _run(self, text: str) -> str:
#         words = len(text.split())
#         return f"Words: {words}"
