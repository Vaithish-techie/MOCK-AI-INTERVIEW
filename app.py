# app.py
from flask import Flask, render_template, session, request, jsonify, send_from_directory
from flask_cors import CORS
from routes.chat import chat_bp
from routes.execution import execution_bp
from routes.external_coding import external_coding_bp
from routes.results import results_bp
from routes.rounds import rounds_bp
from routes.database import database_bp
from routes.ai_feedback import ai_feedback_bp
from routes.behavioral import behavioral_bp
from routes.signup import signup_bp  # New import for sign-up/login
from extensions import db
import config
import time
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = config.SECRET_KEY  # Must be a secure, random string
    app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SESSION_COOKIE_HTTPONLY"] = True  # Prevent JavaScript access to session cookie
    app.config["SESSION_COOKIE_SECURE"] = False  # Set to True in production with HTTPS
    app.config["SESSION_COOKIE_SAMESITE"] = 'Lax'  # Prevent CSRF
    # Specify allowed origins for CORS
    CORS(app, supports_credentials=True, origins=["http://localhost:5000"])
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(chat_bp, url_prefix="/api")
    app.register_blueprint(execution_bp, url_prefix="/api")
    app.register_blueprint(external_coding_bp, url_prefix="/api")
    app.register_blueprint(results_bp, url_prefix="/api")
    app.register_blueprint(rounds_bp, url_prefix="/api")
    app.register_blueprint(database_bp, url_prefix="/api")
    app.register_blueprint(ai_feedback_bp, url_prefix="/api")
    app.register_blueprint(behavioral_bp, url_prefix='/api')
    app.register_blueprint(signup_bp, url_prefix='/api')  # Register new signup blueprint

    # Global error handler for 404 errors
    @app.errorhandler(404)
    def not_found(error):
        logger.error(f"404 Error: {str(error)}")
        return jsonify({"error": "Not found", "message": "The requested URL was not found on the server."}), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        logger.error(f"500 Error: {str(error)}\n{traceback.format_exc()}")
        return jsonify({"error": "Internal server error", "message": "An unexpected error occurred on the server."}), 500

    # Favicon route
    @app.route('/favicon.ico')
    def favicon():
        try:
            logger.debug("Serving favicon from static directory")
            return send_from_directory('static', 'favicon.ico', mimetype='image/x-icon')
        except Exception as e:
            logger.error(f"Error serving favicon: {str(e)}\n{traceback.format_exc()}")
            return jsonify({"error": "Favicon not found"}), 404    

    # Check authentication status
    @app.route('/api/check_auth')
    def check_auth():
        if 'user_id' in session:
            logger.info(f"User authenticated: {session['username']}")
            return jsonify({"authenticated": True, "username": session['username']}), 200
        logger.info("No user authenticated")
        return jsonify({"authenticated": False}), 401

    @app.route("/")
    def index():
        try:
            if "start_time" not in session:
                session["start_time"] = time.time()
            if "performance" not in session:
                session["performance"] = {"hints": 0, "errors": 0, "time_taken": 0, "behavioral_traits": []}
            logger.debug("Rendering index page")
            return render_template("index.html")
        except Exception as e:
            logger.error(f"Error rendering index.html: {str(e)}\n{traceback.format_exc()}")
            return jsonify({"error": "Failed to render page", "message": str(e)}), 500

    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        try:
            db.create_all()
            logger.debug("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {str(e)}\n{traceback.format_exc()}")
            raise
    try:
        logger.info("Starting Flask server on 0.0.0.0:5000")
        app.run(debug=True, use_reloader=False, host="0.0.0.0", port=5000)
    except Exception as e:
        logger.error(f"Server startup failed: {str(e)}\n{traceback.format_exc()}")
        raise