"""Entry point for the Agents app.

Starts the Flask development server on port 8003.
"""

import sys
from pathlib import Path

# Make shared module importable (shared is at ../shared/)
APP_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_ROOT.parent))
sys.path.insert(0, str(APP_ROOT))

from web.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8003, debug=True)
