"""
Configuration for the Chatbot App.

Instantiates a ConfigManager for this application, loading settings
from config.json and environment variables.
"""

import sys
from pathlib import Path

# Add the parent directory (web-based-course/) to sys.path so shared is importable
_app_root = Path(__file__).resolve().parent
_project_root = _app_root.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from shared.config_manager import ConfigManager  # noqa: E402

# Create the config manager instance for this app
config = ConfigManager(_app_root)
