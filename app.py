# app.py
from flask import Flask, render_template, session, request, jsonify
from flask_cors import CORS
from routes.chat import chat_bp
from routes.execution import execution_bp
from routes.external_coding import external_coding_bp
from routes.results import results_bp
from routes.rounds import rounds_bp
from routes.database import database_bp
from routes.ai_feedback import ai_feedback_bp
from routes.behavioral import behavioral_bp
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
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    CORS(app)
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

    # Global error handler for 500 errors
    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "Internal server error occurred. Please try again later."}), 500

    @app.route("/")
    def index():
        if "start_time" not in session:
            session["start_time"] = time.time()
        if "performance" not in session:
            session["performance"] = {"hints": 0, "errors": 0, "time_taken": 0, "behavioral_traits": []}
        return render_template("index.html")

    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()     
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=5000)