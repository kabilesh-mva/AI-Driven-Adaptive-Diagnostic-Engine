# 🧠 AI-Driven Adaptive Diagnostic Engine

An intelligent assessment system that adapts question difficulty in real-time based on student performance, powered by FastAPI and Google's Gemini AI for personalized study recommendations.

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Adaptive Algorithm](#adaptive-algorithm)
- [AI Log](#ai-log)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

- **Adaptive Difficulty**: Questions adjust based on real-time performance
- **Personalized Study Plans**: AI-generated recommendations using Google Gemini
- **Real-time Feedback**: Immediate correctness feedback after each answer
- **Progress Tracking**: Visual progress bar and final ability score
- **Modern UI**: Clean, responsive frontend with gradient design

---

## 🛠️ Tech Stack

| Component | Technology                      |
| --------- | ------------------------------- |
| Backend   | FastAPI (Python 3.9+)           |
| Database  | MongoDB                         |
| AI/ML     | Google Gemini API               |
| Frontend  | HTML5, CSS3, Vanilla JavaScript |
| Server    | Uvicorn (ASGI)                  |

---

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- MongoDB (local or Atlas connection)
- Google Gemini API key

### Step 1: Clone and Setup Virtual Environment

```bash
cd "AI-Driven Adaptive Diagnostic Engine"
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create a `.env` file in the project root:

```env
MONGODB_URI=mongodb://localhost:27017
# Or for MongoDB Atlas:
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority

GEMINI_API_KEY=your_gemini_api_key_here
```

> Get your Gemini API key from: https://makersuite.google.com/app/apikey

---

## 🚀 Running the Application

### 1. Start MongoDB (if running locally)

```bash
# Windows (if MongoDB is installed as a service)
net start MongoDB

# Or run mongod directly
mongod --dbpath "C:\data\db"
```

### 2. Start the Backend Server

```bash
uvicorn main:app --reload
```

The API will be available at: **http://127.0.0.1:8000**

### 3. Open the Frontend

Open `frontend.html` in your browser, or serve it:

```bash
# Option 1: Simple Python HTTP server
python -m http.server 3000

# Then open: http://localhost:3000/frontend.html
```

### 4. API Documentation

Visit **http://127.0.0.1:8000/docs** for interactive API documentation (Swagger UI).

---

## 📡 API Endpoints

| Method | Endpoint                            | Description                         |
| ------ | ----------------------------------- | ----------------------------------- |
| `POST` | `/start-session/{user_id}`          | Create a new assessment session     |
| `GET`  | `/next-question/{session_id}`       | Get the next adaptive question      |
| `POST` | `/submit-answer`                    | Submit an answer and update ability |
| `POST` | `/generate-study-plan/{session_id}` | Generate AI study plan              |

---

## 🧮 Adaptive Algorithm

### Overview

The adaptive engine uses a **simplified Item Response Theory (IRT)** approach to estimate student ability and select appropriately challenging questions.

### Algorithm Logic

```
1. INITIALIZATION
   - Start all users at ability = 0.5 (neutral midpoint)
   - Difficulty range: 0.1 (easiest) to 1.0 (hardest)

2. QUESTION SELECTION
   - Target difficulty = current_ability ± 0.2
   - This creates the "zone of proximal development"
   - Questions already answered are excluded from selection

3. ABILITY UPDATE
   After each answer:

   If CORRECT:
   - Increase ability score
   - Larger boost for harder questions

   If INCORRECT:
   - Decrease ability score
   - Larger drop for easier questions

4. CONVERGENCE
   - After 10 questions, final ability is calculated
   - Score represents estimated student proficiency level
```

### Key Formulas

```python
# Simplified ability update (pseudo-code)
if is_correct:
    new_ability = current_ability + (difficulty * learning_rate)
else:
    new_ability = current_ability - ((1 - difficulty) * learning_rate)

# learning_rate decreases as more questions are answered
# This ensures stability in later stages
```

### Difficulty Bands

| Ability Score | Difficulty Level | Question Range |
| ------------- | ---------------- | -------------- |
| 0.1 - 0.3     | Beginner         | 0.1 - 0.3      |
| 0.3 - 0.5     | Intermediate     | 0.3 - 0.5      |
| 0.5 - 0.7     | Advanced         | 0.5 - 0.7      |
| 0.7 - 0.9     | Expert           | 0.7 - 1.0      |

---

## 🤖 AI Log

### How AI Tools Accelerated Development

#### 1. **Cursor/ChatGPT for Boilerplate Code**

- **Use Case**: Generated FastAPI route templates, Pydantic models, and MongoDB connection setup
- **Time Saved**: ~2-3 hours on initial scaffolding
- **Prompt Example**: "Create a FastAPI endpoint that retrieves questions from MongoDB based on difficulty range"

#### 2. **AI for Algorithm Design**

- **Use Case**: Helped design the adaptive ability estimation formula
- **Challenge**: AI provided textbook IRT formulas that were too complex
- **Solution**: Simplified to a custom weighted update system based on AI suggestions

#### 3. **Google Gemini Integration**

- **Use Case**: AI suggested using `google.generativeai` package
- **Challenge**: Package was deprecated mid-development
- **Resolution**: Manually migrated to `google.genai` (new package) - AI documentation was outdated

#### 4. **Frontend Styling**

- **Use Case**: Generated CSS gradient designs and responsive layouts
- **Time Saved**: ~1 hour on UI polish

### Challenges AI Couldn't Solve

| Challenge                     | AI Limitation                                 | Human Solution                                       |
| ----------------------------- | --------------------------------------------- | ---------------------------------------------------- |
| **Package Deprecation**       | AI suggested deprecated `google.generativeai` | Manually researched and migrated to `google.genai`   |
| **MongoDB Connection Issues** | Generic troubleshooting suggestions           | Debugged connection string and network configuration |
| **State Management Bugs**     | Couldn't trace session state issues           | Used logging to identify missing `is_correct` field  |
| **Python Version Warnings**   | Suggested upgrades that broke dependencies    | Suppressed warnings, documented for future upgrade   |

### Lessons Learned

1. **AI is excellent for**: Boilerplate, documentation, initial drafts
2. **AI struggles with**: Cutting-edge package changes, project-specific debugging
3. **Best Practice**: Always verify AI suggestions against official documentation

---

## 🔧 Troubleshooting

### Common Issues

#### 1. `AttributeError: 'DatabaseManager' object has no attribute 'seed_questions'`

**Fix**: Ensure all methods in `database.py` are properly indented inside the class.

#### 2. `ImportError: cannot import name 'genai' from 'google'`

**Fix**: Install the correct package:

```bash
pip install google-genai
```

#### 3. Questions Repeating

**Fix**: The system now tracks answered questions. If this occurs, clear your MongoDB session collection:

```bash
db.sessions.deleteMany({})
```

#### 4. Python Version Warnings

The application works with Python 3.9, but you'll see deprecation warnings. To eliminate them:

- Upgrade to Python 3.10+
- Or ignore the warnings (they don't affect functionality)

### Getting Help

- Check backend logs in the terminal running `uvicorn`
- Open browser DevTools (F12) for frontend errors
- Visit `/docs` endpoint for API testing

---

## 📄 License

This project is for educational purposes.

---

## 👥 Credits

Developed as part of an AI-driven educational technology project.

**Special Thanks**: Google Gemini API, FastAPI community, MongoDB
