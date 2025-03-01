from extensions import db

class GeneralQuestion(db.Model):
    __tablename__ = "general_questions"
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(500), nullable=False)
    option_a = db.Column(db.String(100), nullable=False)
    option_b = db.Column(db.String(100), nullable=False)
    option_c = db.Column(db.String(100), nullable=False)
    option_d = db.Column(db.String(100), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)

class CodingQuestion(db.Model):
    __tablename__ = "coding_questions"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    topic = db.Column(db.String(50))# models.py
from extensions import db

class GeneralQuestion(db.Model):
    __tablename__ = 'general_question'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)

class CodingQuestion(db.Model):
    __tablename__ = 'coding_question'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(10), nullable=False)
    sample_input = db.Column(db.Text)
    sample_output = db.Column(db.Text)
    sample_input = db.Column(db.String(500))
    sample_output = db.Column(db.String(500))

class BehavioralQuestion(db.Model):
    __tablename__ = "behavioral_questions"
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(500), nullable=False)