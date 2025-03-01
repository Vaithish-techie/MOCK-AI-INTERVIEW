# routes/signup.py
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from extensions import db
import logging
import traceback

signup_bp = Blueprint('signup', __name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@signup_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        logger.debug(f"Received signup data: {data}")
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not all([username, email, password]):
            logger.warning("Missing required fields in signup request")
            return jsonify({"error": "Missing required fields (username, email, or password)"}), 400

        # Check if username or email already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            logger.warning(f"Signup failed: Username '{username}' already exists")
            return jsonify({"error": "Username already exists"}), 400

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            logger.warning(f"Signup failed: Email '{email}' already exists")
            return jsonify({"error": "Email already exists"}), 400

        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')  # Using pbkdf2:sha256 for better security

        # Create new user
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        logger.info(f"New user registered successfully: {username}")

        return jsonify({"message": "User registered successfully", "username": username}), 201

    except Exception as e:
        logger.error(f"Signup error: {str(e)}\n{traceback.format_exc()}")
        db.session.rollback()
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500

@signup_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        logger.debug(f"Received login data: {data}")
        username = data.get('username')
        password = data.get('password')

        if not all([username, password]):
            logger.warning("Missing username or password in login request")
            return jsonify({"error": "Missing username or password"}), 400

        # Check if user exists and password matches
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            logger.warning(f"Login failed: Invalid username or password for username '{username}'")
            return jsonify({"error": "Invalid username or password"}), 401

        # Store user in session (for authentication)
        session['user_id'] = user.id
        session['username'] = user.username
        session.modified = True
        logger.info(f"User logged in successfully: {username}")

        return jsonify({"message": "Login successful", "username": username}), 200

    except Exception as e:
        logger.error(f"Login error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": f"Login failed: {str(e)}"}), 500

@signup_bp.route('/logout', methods=['POST'])
def logout():
    try:
        if 'user_id' in session:
            username = session['username']
            session.pop('user_id', None)
            session.pop('username', None)
            session.modified = True
            logger.info(f"User logged out successfully: {username}")
            return jsonify({"message": "Logged out successfully"}), 200
        logger.warning("Logout failed: No user logged in")
        return jsonify({"error": "No user logged in"}), 401
    except Exception as e:
        logger.error(f"Logout error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": f"Logout failed: {str(e)}"}), 500