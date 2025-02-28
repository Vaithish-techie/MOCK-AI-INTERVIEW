from flask import Flask, render_template, session, request, jsonify
from flask_cors import CORS
from routes.chat import chat_bp
from routes.execution import execution_bp
from routes.external_coding import external_coding_bp
from routes.results import results_bp
from routes.rounds import rounds_bp
from routes.database import database_bp
from routes.ai_feedback import ai_feedback_bp
from extensions import db
import config
import time

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

    @app.route("/")
    def index():
        # Start the timer when the user begins the interview
        if "start_time" not in session:
            session["start_time"] = time.time()
        return render_template("index.html")

    @app.route("/round2")
    def round2():
        return render_template("round2.html")

    @app.route("/api/final_report", methods=["GET"])
    def final_report_with_time():
        # Calculate time taken since the interview started
        start_time = session.get("start_time", time.time())
        time_taken = int((time.time() - start_time) / 60)  # Convert seconds to minutes
        if "performance" not in session:
            session["performance"] = {"hints": 0, "errors": 0, "time_taken": 0, "behavioral_traits": []}
        session["performance"]["time_taken"] = time_taken
        return results_bp.final_report()

    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=5000)
