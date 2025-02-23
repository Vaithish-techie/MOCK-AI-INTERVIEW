# app.py
from flask import Flask, render_template
from flask_cors import CORS
import config
from extensions import db

def create_app():
    # We assume templates and static folders are at the project root inside templates/ and static/
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config)
    CORS(app)
    db.init_app(app)

    @app.route("/")
    def index():
        return render_template("index.html")

    # Import and register our blueprints (all API endpoints)
    from routes.rounds import rounds_bp
    from routes.external_coding import external_coding_bp
    from routes.execution import execution_bp
    from routes.ai_feedback import ai_feedback_bp

    # These endpoints will be called via AJAX from our single-page HTML
    app.register_blueprint(rounds_bp, url_prefix="/api")
    app.register_blueprint(external_coding_bp, url_prefix="/api")
    app.register_blueprint(execution_bp, url_prefix="/api")
    app.register_blueprint(ai_feedback_bp, url_prefix="/api")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
