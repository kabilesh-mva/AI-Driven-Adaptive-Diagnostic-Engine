from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from models import AnswerSubmission
from database import DatabaseManager
from adaptive_engine import AdaptiveEngine
from ai_insights import AIInsightsGenerator  # Import our new AI module

# Load environment variables
load_dotenv()

app = FastAPI(title="AI-Driven Adaptive Diagnostic Engine")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db_manager = DatabaseManager()
adaptive_engine = AdaptiveEngine()
ai_generator = AIInsightsGenerator()  # Initialize AI generator

@app.on_event("startup")
def startup_event():
    """Initialize the database with questions on startup"""
    db_manager.seed_questions()

@app.get("/")
async def root():
    return {"message": "AI-Driven Adaptive Diagnostic Engine API"}

@app.post("/start-session/{user_id}")
async def start_session(user_id: str):
    """Start a new assessment session for a user"""
    session = db_manager.create_session(user_id)
    return {"session_id": session["session_id"], "message": "Session started successfully"}

@app.get("/next-question/{session_id}")
async def get_next_question(session_id: str):
    """Get the next question for the user based on their current ability"""
    session = db_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session["completed"]:
        raise HTTPException(status_code=400, detail="Session already completed")

    current_ability = session["current_ability"]

    # Get list of already answered question IDs
    answered_question_ids = [qa["question_id"] for qa in session["questions_answered"]]

    # Define difficulty range around current ability for optimal challenge
    min_diff = max(0.1, current_ability - 0.2)
    max_diff = min(0.9, current_ability + 0.2)

    # Get questions in the appropriate difficulty range, excluding already answered
    available_questions = db_manager.get_questions_by_difficulty_range(min_diff, max_diff)
    
    # Filter out questions that have already been answered
    available_questions = [q for q in available_questions if q["id"] not in answered_question_ids]

    if not available_questions:
        # Fallback: get closest difficulty questions, excluding already answered
        all_questions = list(db_manager.questions_collection.find().sort([
            ("difficulty", 1)
        ]))
        available_questions = [q for q in all_questions if q["id"] not in answered_question_ids]

    if available_questions:
        # For now, return the first available question
        # In practice, you might want to randomize or apply additional selection criteria
        question = available_questions[0]
        return {
            "question_id": question["id"],
            "text": question["text"],
            "options": question["options"],
            "current_ability": current_ability,
            "estimated_difficulty": question["difficulty"]
        }
    else:
        raise HTTPException(status_code=404, detail="No questions available")

@app.post("/submit-answer")
async def submit_answer(answer_submission: AnswerSubmission):
    """Submit an answer and update the user's ability score"""
    session = db_manager.get_session(answer_submission.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session["completed"]:
        raise HTTPException(status_code=400, detail="Session already completed")
    
    # Get the question to check the answer
    question = db_manager.get_question_by_id(answer_submission.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if answer is correct
    is_correct = answer_submission.selected_answer == question["correct_answer"]
    
    # Record the response
    response_record = {
        "question_id": answer_submission.question_id,
        "selected_answer": answer_submission.selected_answer,
        "correct_answer": question["correct_answer"],
        "is_correct": is_correct,
        "question_difficulty": question["difficulty"]
    }
    
    updated_questions_answered = session["questions_answered"] + [response_record]
    
    # Update ability using the adaptive engine
    new_ability = adaptive_engine.update_ability_estimate(
        session["current_ability"],
        question["difficulty"],
        is_correct,
        len(updated_questions_answered)
    )
    
    # Update session data
    update_data = {
        "current_ability": new_ability,
        "questions_answered": updated_questions_answered,
        "current_question_index": len(updated_questions_answered)
    }
    
    # Check if test is complete (10 questions as per requirements)
    if len(updated_questions_answered) >= 10:
        update_data["completed"] = True
        update_data["final_ability_score"] = new_ability
    
    db_manager.update_session(answer_submission.session_id, update_data)
    
    return {
        "success": True,
        "is_correct": is_correct,
        "updated_ability": new_ability,
        "questions_answered_count": len(updated_questions_answered),
        "test_completed": len(updated_questions_answered) >= 10
    }

@app.post("/generate-study-plan/{session_id}")
async def generate_study_plan(session_id: str):
    """Generate a personalized study plan based on user's performance"""
    session = db_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session["completed"]:
        raise HTTPException(status_code=400, detail="Session not completed yet")
    
    # Analyze performance by topic
    questions_answered = session["questions_answered"]
    
    # Group results by topic
    topic_performance = {}
    for qa in questions_answered:
        # Get the original question to determine its topic
        question = db_manager.get_question_by_id(qa["question_id"])
        if question:
            topic = question["topic"]
            
            if topic not in topic_performance:
                topic_performance[topic] = {"correct": 0, "total": 0}
            
            topic_performance[topic]["total"] += 1
            if qa["is_correct"]:
                topic_performance[topic]["correct"] += 1
    
    # Identify weak areas (topics with <70% accuracy)
    weak_topics = []
    for topic, perf in topic_performance.items():
        accuracy = perf["correct"] / perf["total"]
        if accuracy < 0.7:  # Consider topics with <70% accuracy as weak
            weak_topics.append(topic)
    
    # Prepare data for AI analysis
    performance_summary = {
        "overall_accuracy": sum(1 for q in questions_answered if q["is_correct"]) / len(questions_answered),
        "weak_topics": weak_topics,
        "final_ability_score": session["final_ability_score"],
        "topics_reviewed": list(topic_performance.keys())
    }
    
    try:
        # Generate personalized study plan using Gemini
        ai_result = ai_generator.generate_study_plan(performance_summary)
        
        return {
            "study_plan": ai_result["study_plan"],
            "performance_analysis": ai_result["analysis"],
            "raw_ai_response": ai_result.get("raw_response", "")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating study plan: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)