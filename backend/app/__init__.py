from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

# Load environment variables before loading application configuration.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from .config import Config
from .models.ticket import init_db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS on all routes for all origins
    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        supports_credentials=False,
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    )

    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = app.make_default_options_response()
            origin = request.headers.get("Origin", "*")
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            return response

    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get("Origin") or "*"
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        return response

    @app.route("/")
    def index():
        return jsonify({
            "status": "online",
            "message": "SmartDesk AI API is running"
        })

    from .routes.ticket_routes import ticket_bp
    app.register_blueprint(ticket_bp, url_prefix="/api")
    app.register_blueprint(ticket_bp, name="tickets_root")

    init_db(app.config["DATABASE"])

    return app
