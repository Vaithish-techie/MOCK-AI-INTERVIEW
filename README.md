A web-based platform for simulating technical interviews. The application integrates multiple rounds—including MCQs and coding challenges—with real-time code execution and AI-powered code analysis. This tool is designed to help candidates prepare for technical interviews in a professional, interactive environment.

Features
Round 1: Technical MCQs
Randomly fetches and displays 5–10 MCQs from a seeded database.
Real-time progress tracking and immediate feedback upon submission.

Round 2: Coding Challenge
Retrieves 2 balanced coding challenges from the database (e.g., one easy and one hard, or two medium problems).
Provides a large code editor for each challenge.
Supports code execution (via Judge0 API or a local alternative) with output displayed.
Offers AI-powered code analysis (using OpenAI or local models) with results shown alongside output.

Final Report
Displays performance graphs, achievement badges, and a leaderboard (if multiplayer mode is enabled).
Provides detailed analysis and a transcript of the interview session.
Responsive & Interactive UI

Modern dark theme with professional styling.
Clear visual separation between different rounds and interactive elements like hover effects.

Technologies Used
Backend: Python, Flask, Flask-SQLAlchemy, Flask-Cors
Database: PostgreSQL
APIs: Judge0 for code execution, OpenAI (or local alternatives) for AI analysis
Frontend: HTML, CSS, JavaScript, Chart.js (for final report graphs)
Deployment: (Local development; can be extended to AWS, Docker, etc.)

Project Structure
Mock-AI-Interview/
├── .env.example                # Example environment variables file
├── .gitignore                  # Specifies files and directories to ignore
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── app.py                      # Flask application entry point
├── config.py                   # Application configuration (loads .env)
├── extensions.py               # Flask extensions initialization (e.g., SQLAlchemy)
├── models.py                   # Database models (MCQs, Coding Questions, etc.)
├── seed.py                     # Script to seed the database with questions
├── routes/
│   ├── __init__.py
│   ├── rounds.py               # API endpoints for MCQs (Round 1)
│   ├── external_coding.py      # API endpoint for balanced coding challenges (Round 2)
│   ├── execution.py            # API endpoint for code execution
│   └── ai_feedback.py          # API endpoint for AI-powered code analysis
├── static/
│   ├── css/
│   │   └── styles.css          # CSS for the frontend
│   └── js/
│       └── script.js           # JavaScript for UI interactions & API calls
└── templates/
    └── index.html              # Single-page HTML for the UI

Installation and Setup
Clone the Repository
git clone https://github.com/yourusername/Mock-AI-Interview.git
cd Mock-AI-Interview
Create and Activate a Virtual Environment

On Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate

On macOS/Linux:
python3 -m venv venv
source venv/bin/activate

Install Dependencies
pip install -r requirements.txt

Configure Environment Variables
Copy the .env.example file to .env:
cp .env.example .env
Edit .env to include your secrets (e.g., SECRET_KEY, SQLALCHEMY_DATABASE_URI, JUDGE0_API_KEY, OPENAI_API_KEY).

Set Up the Database
Ensure PostgreSQL is running.
Create a database (e.g., interview_db).
Run the seed script to populate the database:
python -m seed

Run the Application
python -m app
Open your browser and navigate to http://127.0.0.1:5000/.

Usage
Dashboard:
Landing page with navigation options for each round.

Round 1 (MCQs):
Answer a set of technical MCQs. Your progress is tracked, and you receive feedback upon submission.

Round 2 (Coding Challenges):
Two coding challenges are displayed with the question on the left and a large code editor on the right.
Click "Run Code" to execute your solution and see the output.
Click "AI Analysis" to receive automated code analysis feedback.

Final Report:
View your performance summary, including performance graphs, achievement badges, and a leaderboard.

Git and Environment Management
.gitignore:
The repository includes a .gitignore file to prevent committing:
Virtual environment directories (e.g., venv/, Lib/, Scripts/, etc.)
Environment variable files (.env)
Cache files (__pycache__/, *.pyc)
Other system-specific or IDE files

Environment Variables:
We use python-dotenv to load configuration from a .env file. Do not commit your actual .env file; instead, use .env.example as a template.
