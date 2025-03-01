# backend/seed.py
from app import create_app
from extensions import db
from models import GeneralQuestion, CodingQuestion

app = create_app()

with app.app_context():
    db.create_all()

    # Define 20 important general MCQ questions
    mcq_data = [
        {
            "category": "DSA",
            "question_text": "What is the time complexity of binary search in a sorted array?",
            "option_a": "O(n)",
            "option_b": "O(log n)",
            "option_c": "O(n log n)",
            "option_d": "O(1)",
            "correct_option": "B"
        },
        {
            "category": "DSA",
            "question_text": "Which data structure is used in Breadth First Search (BFS)?",
            "option_a": "Stack",
            "option_b": "Queue",
            "option_c": "Tree",
            "option_d": "Graph",
            "correct_option": "B"
        },
        {
            "category": "OS",
            "question_text": "What is the primary function of a scheduler in an operating system?",
            "option_a": "Memory management",
            "option_b": "Process scheduling",
            "option_c": "Input/Output handling",
            "option_d": "File system management",
            "correct_option": "B"
        },
        {
            "category": "OS",
            "question_text": "Which of the following is a type of CPU scheduling algorithm?",
            "option_a": "First Come First Serve",
            "option_b": "Shortest Job Next",
            "option_c": "Round Robin",
            "option_d": "All of the above",
            "correct_option": "D"
        },
        {
            "category": "DBMS",
            "question_text": "What does ACID stand for in database transactions?",
            "option_a": "Atomicity, Consistency, Isolation, Durability",
            "option_b": "Accuracy, Consistency, Isolation, Durability",
            "option_c": "Atomicity, Concurrency, Isolation, Durability",
            "option_d": "Atomicity, Consistency, Integration, Durability",
            "correct_option": "A"
        },
        {
            "category": "DBMS",
            "question_text": "Which SQL statement is used to retrieve data from a database?",
            "option_a": "SELECT",
            "option_b": "INSERT",
            "option_c": "UPDATE",
            "option_d": "DELETE",
            "correct_option": "A"
        },
        {
            "category": "Networking",
            "question_text": "Which protocol is used for secure communication over the internet?",
            "option_a": "HTTP",
            "option_b": "FTP",
            "option_c": "SSH",
            "option_d": "HTTPS",
            "correct_option": "D"
        },
        {
            "category": "Networking",
            "question_text": "What does DNS stand for?",
            "option_a": "Domain Name System",
            "option_b": "Data Network Service",
            "option_c": "Digital Number System",
            "option_d": "Domain Number Service",
            "correct_option": "A"
        },
        {
            "category": "Programming Concepts",
            "question_text": "What is polymorphism in Object-Oriented Programming?",
            "option_a": "Ability of a function to call itself",
            "option_b": "Ability of different classes to be treated as instances of the same class",
            "option_c": "Encapsulation of data",
            "option_d": "None of the above",
            "correct_option": "B"
        },
        {
            "category": "Programming Concepts",
            "question_text": "What is recursion?",
            "option_a": "A function calling itself",
            "option_b": "A loop that repeats a fixed number of times",
            "option_c": "A data structure",
            "option_d": "None of the above",
            "correct_option": "A"
        },
        {
            "category": "DSA",
            "question_text": "Which sorting algorithm has the best average-case performance?",
            "option_a": "Bubble Sort",
            "option_b": "Insertion Sort",
            "option_c": "Merge Sort",
            "option_d": "Selection Sort",
            "correct_option": "C"
        },
        {
            "category": "DSA",
            "question_text": "Which data structure is used to implement a LIFO (Last In First Out) behavior?",
            "option_a": "Queue",
            "option_b": "Stack",
            "option_c": "Linked List",
            "option_d": "Tree",
            "correct_option": "B"
        },
        {
            "category": "OS",
            "question_text": "Which of the following is not a scheduling algorithm?",
            "option_a": "FCFS",
            "option_b": "SJF",
            "option_c": "RR",
            "option_d": "FIFO",
            "correct_option": "D"
        },
        {
            "category": "OS",
            "question_text": "What is a context switch?",
            "option_a": "Switching between different CPU cores",
            "option_b": "Switching from one process or thread to another",
            "option_c": "Switching the operating system",
            "option_d": "None of the above",
            "correct_option": "B"
        },
        {
            "category": "DBMS",
            "question_text": "What is a primary key in a database?",
            "option_a": "A unique identifier for table records",
            "option_b": "A column that can have duplicate values",
            "option_c": "A key used for foreign key relationships",
            "option_d": "None of the above",
            "correct_option": "A"
        },
        {
            "category": "DBMS",
            "question_text": "What is normalization in databases?",
            "option_a": "Process of denormalizing data for performance",
            "option_b": "Process of organizing data to reduce redundancy",
            "option_c": "Process of indexing data",
            "option_d": "None of the above",
            "correct_option": "B"
        },
        {
            "category": "Networking",
            "question_text": "What port does HTTP use by default?",
            "option_a": "21",
            "option_b": "80",
            "option_c": "443",
            "option_d": "8080",
            "correct_option": "B"
        },
        {
            "category": "Networking",
            "question_text": "Which device is used to connect multiple networks?",
            "option_a": "Switch",
            "option_b": "Router",
            "option_c": "Hub",
            "option_d": "Bridge",
            "correct_option": "B"
        },
        {
            "category": "Programming Concepts",
            "question_text": "What is an API?",
            "option_a": "Application Programming Interface",
            "option_b": "Application Process Interface",
            "option_c": "Advanced Programming Instruction",
            "option_d": "None of the above",
            "correct_option": "A"
        },
        {
            "category": "Programming Concepts",
            "question_text": "What does MVC stand for in web development?",
            "option_a": "Model-View-Controller",
            "option_b": "Model-View-Container",
            "option_c": "Module-View-Controller",
            "option_d": "None of the above",
            "correct_option": "A"
        }
    ]

    # Seed Coding Questions (Round 2) – if desired, here are 2 examples:
    coding_questions = [
        {
            "title": "Reverse a String",
            "description": "Write a function to reverse a given string.",
            "difficulty": "Easy",
            "sample_input": "hello",
            "sample_output": "olleh"
        },
        {
            "title": "Find Maximum Number",
            "description": "Find the maximum number in a given list.",
            "difficulty": "Medium",
            "sample_input": "3 5 1 8",
            "sample_output": "8"
        }
    ]

    # Add MCQs
    for q in mcq_data:
        new_q = GeneralQuestion(
            category=q["category"],
            question_text=q["question_text"],
            option_a=q["option_a"],
            option_b=q["option_b"],
            option_c=q["option_c"],
            option_d=q["option_d"],
            correct_option=q["correct_option"]
        )
        db.session.add(new_q)

    # Add Coding Questions
    for cq in coding_questions:
        new_cq = CodingQuestion(
            title=cq["title"],
            description=cq["description"],
            difficulty=cq["difficulty"],
            sample_input=cq["sample_input"],
            sample_output=cq["sample_output"]
        )
        db.session.add(new_cq)

    db.session.commit()
    print("Database seeded successfully!")
