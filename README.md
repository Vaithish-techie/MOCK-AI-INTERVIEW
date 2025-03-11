# Mock AI Interview

Mock AI Interview is a web-based platform designed to simulate technical interview rounds, including MCQs and coding challenges. The platform features real-time code execution and AI-powered analysis to help candidates prepare effectively in an interactive environment.

## Features

### Round 1: Technical MCQs
- Randomly fetches 5–10 MCQs from a seeded database.
- Real-time progress tracking and instant feedback.

### Round 2: Coding Challenge
- Retrieves 2 coding challenges (balanced difficulty levels).
- Integrated code editor for solving challenges.
- Supports real-time code execution via Judge0 API.
- AI-powered code analysis with feedback.

### Final Report
- Performance summary with graphs and achievement badges.
- Leaderboard support (if multiplayer mode is enabled).
- Detailed analysis and session transcript.

### UI & Design
- Modern dark-themed interface.
- Intuitive layout with interactive elements.

## Technologies Used

- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-CORS
- **Database:** PostgreSQL
- **APIs:** Judge0 (code execution)
- **LLM:** Mistral‑7B‑Instruct‑v0.1 (via Transformers & BitsAndBytes for 4-bit quantization)
- **Frontend:** HTML, CSS, JavaScript, Chart.js (for report graphs)
- **Deployment:** Local development (extendable to AWS, Docker, etc.)

## Project Structure

```
Mock-AI-Interview/
├── .env.example        # Sample environment variables
├── .gitignore          # Git ignore list
├── README.md           # Project documentation
├── requirements.txt    # Python dependencies
├── app.py              # Application entry point
├── config.py           # Configuration settings
├── extensions.py       # Flask extensions setup
├── models.py           # Database models
├── seed.py             # Script to populate database
├── routes/             # API endpoints
│   ├── rounds.py       # MCQ handling (Round 1)
│   ├── external_coding.py  # Coding challenges (Round 2)
│   ├── results.py    # For real-time results
│   ├── execution.py    # Code execution via Judge0
│   ├── behavioral.py    # For behavioral round
│   ├── chat.py    # Backend for chatbot with LLM integration
│   ├── signup.py    # For login in page
|   └── ai_feedback.py  # AI analysis
├── static/             # Frontend assets
│   ├── css/styles.css  # Stylesheet
│   └── js/script.js    # UI interactions
└── templates/
    └── index.html      # Web interface
```

## Installation & Setup

### Clone the Repository
```sh
git clone https://github.com/yourusername/Mock-AI-Interview.git
cd Mock-AI-Interview
```

### Create & Activate Virtual Environment
#### Windows (PowerShell)
```sh
python -m venv venv
.\venv\Scripts\Activate
```
#### macOS/Linux
```sh
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies
```sh
pip install -r requirements.txt
```

### Configure Environment Variables
```sh
cp .env.example .env
```
Edit `.env` to set up credentials (SECRET_KEY, SQLALCHEMY_DATABASE_URI, JUDGE0_API_KEY, OPENAI_API_KEY).

### Set Up the Database
- Ensure PostgreSQL is running.
- Create a database (e.g., `interview_db`).
- Seed the database:
```sh
python -m seed
```

### Run the Application
```sh
python -m app
```
Visit [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your browser.

## Usage

### Dashboard
- Navigate between different interview rounds.

### Round 1 (MCQs)
- Answer a set of technical MCQs.
- Receive real-time feedback.

### Round 2 (Coding Challenges)
- Solve coding problems using the integrated editor.
- Click **"Run Code"** to execute solutions.
- Click **"AI Analysis"** for automated feedback.
- Click **"Submit"** for code submission.

### Final Report
- View performance analytics.
- Access a detailed session transcript.

## Git & Environment Management

- **`.gitignore`** prevents committing sensitive files (e.g., `.env`, `pycache/`, virtual environments).
- **Environment Variables:** Managed using `python-dotenv`. Use `.env.example` as a reference; do not commit `.env`.

---
This project provides a structured and interactive approach to technical interview preparation. Future enhancements may include additional AI capabilities, extended question banks, and multiplayer interview simulations.

