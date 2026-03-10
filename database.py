from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
import os   
from models import Question, UserSession
import uuid
from datetime import datetime
import logging  

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class DatabaseManager():
    def __init__(self):
        self.client = None
        self.db = None
        self.questions_collection = None
        self.sessions_collection = None
        self.connect()


    def connect(self):
        try:
            mongo_uri = os.getenv("MONGODB_URI")
            if not mongo_uri:
                raise ValueError("MONGODB_URI is not set in environment variables.")
            self.client = MongoClient(mongo_uri)
            self.db = self.client["adaptive_testing"]
            self.questions_collection = self.db.questions
            self.sessions_collection = self.db.sessions
            logger.info("Connected to MongoDB successfully.")
        except ConnectionFailure as e:
            logger.error(f"Could not connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"An error occurred while connecting to MongoDB: {e}")
            raise

    def seed_questions(self):
        """Seeds the database with initial questions if the collection is empty."""
        if self.questions_collection.count_documents({}) == 0:
            questions = [
            # Difficulty 0.1 (Very Easy) - 2 questions
            {
                "id": "q01",
                "text": "What is 2 + 2?",
                "options": ["3", "4", "5", "6"],
                "correct_answer": "4",
                "difficulty": 0.1,
                "topic": "Arithmetic",
                "tags": ["basic-addition"]
            },
            {
                "id": "q02",
                "text": "Which word means 'happy'?",
                "options": ["sad", "joyful", "angry", "tired"],
                "correct_answer": "joyful",
                "difficulty": 0.1,
                "topic": "Vocabulary",
                "tags": ["synonyms"]
            },
            
            # Difficulty 0.2 (Easy) - 2 questions
            {
                "id": "q03",
                "text": "What is 15 divided by 3?",
                "options": ["3", "4", "5", "6"],
                "correct_answer": "5",
                "difficulty": 0.2,
                "topic": "Arithmetic",
                "tags": ["division"]
            },
            {
                "id": "q04",
                "text": "Which word is the opposite of 'hot'?",
                "options": ["warm", "cold", "cool", "freezing"],
                "correct_answer": "cold",
                "difficulty": 0.2,
                "topic": "Vocabulary",
                "tags": ["antonyms"]
            },
            
            # Difficulty 0.3 (Easy-Medium) - 2 questions
            {
                "id": "q05",
                "text": "What is the value of x if 3x + 7 = 22?",
                "options": ["3", "5", "7", "9"],
                "correct_answer": "5",
                "difficulty": 0.3,
                "topic": "Algebra",
                "tags": ["linear-equations"]
            },
            {
                "id": "q06",
                "text": "Which word is most similar in meaning to 'big'?",
                "options": ["small", "large", "tiny", "minuscule"],
                "correct_answer": "large",
                "difficulty": 0.3,
                "topic": "Vocabulary",
                "tags": ["synonyms"]
            },
            
            # Difficulty 0.4 (Medium-Easy) - 2 questions
            {
                "id": "q07",
                "text": "If the area of a circle is 16π square units, what is its circumference?",
                "options": ["4π", "8π", "16π", "32π"],
                "correct_answer": "8π",
                "difficulty": 0.4,
                "topic": "Geometry",
                "tags": ["circles"]
            },
            {
                "id": "q08",
                "text": "Which word best describes someone who is 'gregarious'?",
                "options": ["shy", "outgoing", "arrogant", "confused"],
                "correct_answer": "outgoing",
                "difficulty": 0.4,
                "topic": "Vocabulary",
                "tags": ["adjectives"]
            },
            
            # Difficulty 0.5 (Medium) - 2 questions
            {
                "id": "q09", 
                "text": "Which word best completes the sentence: 'The author so ___ that readers found it difficult to follow.'",
                "options": ["eloquent", "convoluted", "lucid", "straightforward"],
                "correct_answer": "convoluted",
                "difficulty": 0.5,
                "topic": "Vocabulary",
                "tags": ["verbal-reasoning"]
            },
            {
                "id": "q10",
                "text": "What is the next number in the sequence: 2, 6, 18, 54, ...?",
                "options": ["108", "162", "216", "156"],
                "correct_answer": "162",
                "difficulty": 0.5,
                "topic": "Arithmetic",
                "tags": ["sequences"]
            },
            
            # Difficulty 0.6 (Medium-Hard) - 2 questions
            {
                "id": "q11",
                "text": "Solve for x: x² - 5x + 6 = 0",
                "options": ["2, 3", "1, 6", "-2, -3", "-1, -6"],
                "correct_answer": "2, 3",
                "difficulty": 0.6,
                "topic": "Algebra",
                "tags": ["quadratic-equations"]
            },
            {
                "id": "q12",
                "text": "Which word best completes the analogy: WATER : DROWN :: FIRE : ______?",
                "options": ["burn", "ignite", "extinguish", "smoke"],
                "correct_answer": "burn",
                "difficulty": 0.6,
                "topic": "Vocabulary",
                "tags": ["analogies"]
            },
            
            # Difficulty 0.7 (Hard-Medium) - 2 questions
            {
                "id": "q13",
                "text": "Which of the following is equivalent to √(72)?",
                "options": ["6√2", "8√3", "12√3", "6√12"],
                "correct_answer": "6√2",
                "difficulty": 0.7,
                "topic": "Arithmetic",
                "tags": ["radicals"]
            },
            {
                "id": "q14",
                "text": "In a class of 30 students, 18 play soccer, 15 play basketball, and 7 play both. How many play neither sport?",
                "options": ["2", "3", "4", "5"],
                "correct_answer": "4",
                "difficulty": 0.7,
                "topic": "Arithmetic",
                "tags": ["sets", "venn-diagrams"]
            },
            
            # Difficulty 0.8 (Hard) - 2 questions
            {
                "id": "q15",
                "text": "Which of the following represents the solution to |2x - 3| < 7?",
                "options": ["x < 5", "x > -2", "-2 < x < 5", "x < -2 or x > 5"],
                "correct_answer": "-2 < x < 5",
                "difficulty": 0.8,
                "topic": "Algebra",
                "tags": ["absolute-value"]
            },
            {
                "id": "q16",
                "text": "What is the slope of the line perpendicular to 3x + 4y = 12?",
                "options": ["3/4", "4/3", "-3/4", "-4/3"],
                "correct_answer": "4/3",
                "difficulty": 0.8,
                "topic": "Algebra",
                "tags": ["linear-equations", "slope"]
            },
            
            # Difficulty 0.9 (Very Hard) - 2 questions
            {
                "id": "q17",
                "text": "If 2^(x+1) = 16, what is the value of x?",
                "options": ["2", "3", "4", "5"],
                "correct_answer": "3",
                "difficulty": 0.9,
                "topic": "Algebra",
                "tags": ["exponents", "logarithms"]
            },
            {
                "id": "q18",
                "text": "Which word means 'to make less severe'?",
                "options": ["aggravate", "mitigate", "exacerbate", "intensify"],
                "correct_answer": "mitigate",
                "difficulty": 0.9,
                "topic": "Vocabulary",
                "tags": ["verbs"]
            },
            
            # Difficulty 1.0 (Extremely Hard) - 2 questions
            {
                "id": "q19",
                "text": "If the radius of a sphere is doubled, by what factor does its volume increase?",
                "options": ["2", "4", "6", "8"],
                "correct_answer": "8",
                "difficulty": 1.0,
                "topic": "Geometry",
                "tags": ["volume", "spheres"]
            },
            {
                "id": "q20",
                "text": "If x/y = 3/4 and y/z = 2/5, what is x/z?",
                "options": ["3/10", "6/9", "5/9", "2/5"],
                "correct_answer": "3/10",
                "difficulty": 1.0,
                "topic": "Algebra",
                "tags": ["ratios", "fractions"]
            }
        ]

            result = self.questions_collection.insert_many(questions)
            logger.info(f"Seeded {len(result.inserted_ids)} questions into the database.")
        else:
            logger.info("Questions collection already has data. Skipping seeding.")

    def get_question_by_id(self, question_id: str):
        """Retrieves a question from the database by its ID."""
        try:
            question_data = self.questions_collection.find_one({"id": question_id})
            if question_data:
                return question_data
            else:
                logger.warning(f"Question with ID {question_id} not found.")
                return None
        except Exception as e:
            logger.error(f"An error occurred while retrieving question {question_id}: {e}")
            raise

    def get_questions_by_difficulty_range(self, min_diff: float, max_diff: float):
        """Retrieves questions from the database that match a specific difficulty level."""
        try:
            return list(self.questions_collection.find({"difficulty": {"$gte": min_diff, "$lte": max_diff}})
                        .sort("difficulty", 1))
        except Exception as e:
            logger.error(f"An error occurred while retrieving questions with difficulty {min_diff}-{max_diff}: {e}")
            raise

    def create_session(self, user_id: str):
        """Creates a new user session in the database."""
        try:
            session_id = str(uuid.uuid4())
            session_data = {
                "session_id": session_id,
                "user_id": user_id,
                "current_ability": 0.5,  # Starting with a neutral ability estimate
                "current_question_index": 0,
                "started_at": datetime.utcnow(),
                "completed": False,
                "questions_answered": [],
                "final_ability_score": None
            }
            result = self.sessions_collection.insert_one(session_data)
            logger.info(f"Created new session for user: {session_data['session_id']}")
            return session_data
        except Exception as e:
            logger.error(f"An error occurred while creating session for user {user_id}: {e}")
            raise

    def get_session(self, session_id: str):
        """Retrieves a user session from the database by its ID."""
        try:
            session_data = self.sessions_collection.find_one({"session_id": session_id})
            if session_data:
                return session_data
            else:
                logger.warning(f"Session with ID {session_id} not found.")
                return None
        except Exception as e:
            logger.error(f"An error occurred while retrieving session {session_id}: {e}")
            raise

    def update_session(self, session_id: str, update_data: dict):
        """Updates a user session in the database with new data."""
        try:
            result = self.sessions_collection.update_one({"session_id": session_id}, {"$set": update_data})
            if result.modified_count > 0:
                logger.info(f"Updated session {session_id} successfully.")
            else:
                logger.warning(f"No updates made to session {session_id}.")
        except Exception as e:
            logger.error(f"An error occurred while updating session {session_id}: {e}")
            raise   