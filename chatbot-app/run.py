"""
Entry point for the Chatbot App.

Starts the Flask development server on port 8001.
"""

import sys
from pathlib import Path

# Add the parent directory (web-based-course/) to sys.path so shared is importable
_app_root = Path(__file__).resolve().parent
_project_root = _app_root.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Add the app root itself so that 'web' and 'ai' packages are importable
if str(_app_root) not in sys.path:
    sys.path.insert(0, str(_app_root))

from web.app import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True)
