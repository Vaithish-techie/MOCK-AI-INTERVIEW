from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
JUDGE0_API_KEY = os.getenv("JUDGE0_API_KEY")
JUDGE0_BASE_URL = "https://judge0-ce.p.rapidapi.com/submissions"
HF_TOKEN = os.getenv("HF_TOKEN")
# Supported Programming Languages (Judge0 API)
LANGUAGE_MAP = {
    "python": 71,
    "cpp": 54,
    "java": 62
}
