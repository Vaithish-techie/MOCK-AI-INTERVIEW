# backend/seed.py
from app import create_app
from extensions import db
from models import GeneralQuestion, CodingQuestion, BehavioralQuestion

app = create_app()

with app.app_context():
    db.create_all()

    # Define 20 important behavioral questions
    behavioral_questions = [
        {
            "question_text": "Describe a time you faced a challenge at work. Use the STAR method (Situation, Task, Action, Result) to explain."
        },
        {
            "question_text": "Tell me about a time you worked in a team to solve a problem. What was your role, and what was the outcome?"
        },
        {
            "question_text": "Can you share an example of a difficult decision you made? How did you handle it, and what was the result?"
        },
        {
            "question_text": "Describe a situation where you had to meet a tight deadline. How did you prioritize and manage your time?"
        },
        {
            "question_text": "Tell me about a time you failed at a task. What did you learn, and how did you improve?"
        },
        {
            "question_text": "Describe a time you had to deal with a difficult colleague or client. How did you resolve the situation?"
        },
        {
            "question_text": "Can you provide an example of when you took initiative on a project? What actions did you take, and what was the impact?"
        },
        {
            "question_text": "Tell me about a time you had to adapt to a significant change at work. How did you handle it, and what was the result?"
        },
        {
            "question_text": "Describe a situation where you had to persuade others to adopt your idea. What approach did you take, and what was the outcome?"
        },
        {
            "question_text": "Share an instance where you had to manage conflicting priorities. How did you decide what to focus on, and what happened?"
        },
        {
            "question_text": "Tell me about a time you received constructive criticism. How did you respond, and what did you do differently as a result?"
        },
        {
            "question_text": "Describe a time you went above and beyond for a customer or client. What actions did you take, and what was the feedback?"
        },
        {
            "question_text": "Can you recount a time you had to lead a team through a challenging project? What strategies did you use, and what was the result?"
        },
        {
            "question_text": "Tell me about a time you had to learn a new skill or technology quickly. How did you approach it, and what was the outcome?"
        },
        {
            "question_text": "Describe a situation where you had to resolve a conflict within your team. What steps did you take, and what was the resolution?"
        },
        {
            "question_text": "Share an example of when you identified a problem and implemented a solution. What was the problem, and what was the impact of your solution?"
        },
        {
            "question_text": "Tell me about a time you had to handle a high-pressure situation. How did you stay calm, and what was the result?"
        },
        {
            "question_text": "Describe a time you mentored or coached someone. What approach did you take, and how did it benefit the person or team?"
        },
        {
            "question_text": "Can you provide an instance where you improved a process or workflow? What changes did you make, and what were the results?"
        },
        {
            "question_text": "Tell me about a time you had to balance multiple responsibilities. How did you prioritize, and what was the outcome?"
        }
    ]

    # Add Behavioral Questions
    for q in behavioral_questions:
        new_q = BehavioralQuestion(
            question_text=q["question_text"]
        )
        db.session.add(new_q)

    # Commit all changes
    db.session.commit()
    print("Database seeded with behavioral questions successfully!")

    # Note: If you want to clear existing behavioral questions before seeding, uncomment and run:
    # db.session.query(BehavioralQuestion).delete()
    # db.session.commit()