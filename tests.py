from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DB_URI =  os.getenv("SQLALCHEMY_DATABASE_URI")

try:
    engine = create_engine(DB_URI)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        print("✅ Connection to PostgreSQL successful!")
except Exception as e:
    print(f"❌ Failed to connect: {e}")
