from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

# Load environment variables before loading application configuration.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from .config import Config
from .models.ticket import init_db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    frontend_origins = [
        o.strip() for o in app.config.get("FRONTEND_ORIGIN", "").split(",") if o.strip()
    ]
    if not frontend_origins:
        frontend_origins = ["*"]

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": "*" if "*" in frontend_origins else frontend_origins
            }
        }
    )

    from .routes.ticket_routes import ticket_bp
    app.register_blueprint(ticket_bp, url_prefix="/api")

    init_db(app.config["DATABASE"])

    return app
