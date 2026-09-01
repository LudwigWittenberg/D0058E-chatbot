"""
Flask application factory for the Agents App.

Creates and configures the Flask application, registers blueprints,
and sets template/static folder paths.
"""

import os
import sys
from pathlib import Path
from flask import Flask

# Ensure shared module is importable
_app_root = Path(__file__).resolve().parent.parent
_project_root = _app_root.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


def create_app() -> Flask:
    """
    Create and configure the Flask application.

    Returns:
        Configured Flask application instance.
    """
    # Resolve template and static folder paths relative to this file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_folder = os.path.join(base_dir, "templates")
    static_folder = os.path.join(base_dir, "static")

    app = Flask(
        __name__,
        template_folder=template_folder,
        static_folder=static_folder,
    )
    app.secret_key = "agents-app-dev-key"

    # Register the main routes blueprint
    from web.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app
