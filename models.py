from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Question(BaseModel):
    id: str
    text: str
    options: List[str]
    correct_answer: str
    difficulty: float  # 0.1 to 1.0
    topic: str
    tags: List[str]

class UserSession(BaseModel):
    session_id: str
    user_id: str
    current_ability: float = 0.5  # Start at baseline
    questions_answered: List[dict] = []  # Store question_id, answer, is_correct
    current_question_index: int = 0
    started_at: datetime
    completed: bool = False
    final_ability_score: Optional[float] = None

class AnswerSubmission(BaseModel):
    session_id: str
    question_id: str
    selected_answer: str