from google.genai import Client
import os
from dotenv import load_dotenv
import logging
import re

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIInsightsGenerator:
    def __init__(self):
        # Initialize the Gemini API with your key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        # Initialize the client with the API key
        self.client = Client(api_key=api_key)

    def generate_study_plan(self, user_performance_data):
        """
        Generate a personalized 3-step study plan based on user's performance
        """
        # Analyze the user's performance data to identify strengths and weaknesses
        overall_accuracy = user_performance_data.get("overall_accuracy", 0)
        weak_topics = user_performance_data.get("weak_topics", [])
        final_ability_score = user_performance_data.get("final_ability_score", 0.5)
        topics_reviewed = user_performance_data.get("topics_reviewed", [])

        # Create a detailed prompt for Gemini
        prompt = f"""
        You are an expert educational advisor. Based on the student's assessment performance, create a personalized 3-step study plan that addresses their specific needs.

        STUDENT PERFORMANCE SUMMARY:
        - Overall Accuracy: {overall_accuracy:.2%}
        - Final Ability Score: {final_ability_score:.2f} (Scale 0.1-0.9, where 0.1 is lowest, 0.9 is highest)
        - Topics Reviewed: {', '.join(topics_reviewed)}
        - Weak Topics (accuracy < 70%): {', '.join(weak_topics) if weak_topics else 'None identified'}

        Please provide exactly 3 specific, actionable steps for improvement that address:
        1. Focus areas based on weak topics identified
        2. Study strategies appropriate for their ability level
        3. Practice recommendations to improve performance

        Format your response as follows:
        STEP 1: [Concise title] - [Detailed action plan]
        STEP 2: [Concise title] - [Detailed action plan]
        STEP 3: [Concise title] - [Detailed action plan]

        Make the advice practical, specific, and tailored to their performance data.
        """

        try:
            # Generate the study plan using Gemini
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt,
                config={
                    "temperature": 0.7,
                    "max_output_tokens": 500,
                }
            )

            # Extract the generated text
            study_plan_text = response.text

            # Parse the response into 3 steps
            steps = self._parse_study_plan(study_plan_text)

            return {
                "study_plan": steps,
                "raw_response": study_plan_text,
                "analysis": {
                    "overall_accuracy": overall_accuracy,
                    "weak_topics": weak_topics,
                    "final_ability_score": final_ability_score,
                    "topics_reviewed": topics_reviewed
                }
            }

        except Exception as e:
            logger.error(f"Error generating study plan: {e}")
            # Provide a fallback study plan if API call fails
            return self._generate_fallback_plan(user_performance_data)

    def _parse_study_plan(self, study_plan_text):
        """
        Parse the Gemini response into 3 distinct steps
        """
        lines = study_plan_text.strip().split('\n')
        steps = []

        for line in lines:
            line = line.strip()
            # Look for lines that start with a number
            if line.upper().startswith('STEP 1:') or line.upper().startswith('STEP 2:') or line.upper().startswith('STEP 3:'):
                # Extract the content after the STEP label
                if ':' in line:
                    step_content = line.split(':', 1)[1].strip()
                    steps.append(step_content)

        # If parsing didn't work properly, fall back to splitting by sentences
        if len(steps) < 3:
            # Try to extract steps based on common patterns
            step_patterns = [
                r'STEP\s+\d+:\s*(.*?)(?=STEP\s+\d+:|$)',
                r'\d\.\s*(.*?)(?=\d\.|$)',  # Numbered lists like "1. content 2. content"
                r'\*\*\d\.\*\*\s*(.*?)(?=\*\*\d\.\*\*|$)'  # Bold numbered lists
            ]

            for pattern in step_patterns:
                matches = re.findall(pattern, study_plan_text, re.DOTALL | re.IGNORECASE)
                if len(matches) >= 3:
                    steps = [match.strip() for match in matches[:3]]
                    break

        # If still not enough steps, split the text into 3 roughly equal parts
        if len(steps) < 3:
            sentences = study_plan_text.split('. ')
            if len(sentences) >= 3:
                # Join sentences to create 3 approximately equal sections
                chunk_size = len(sentences) // 3
                for i in range(3):
                    start_idx = i * chunk_size
                    if i == 2:  # Last chunk gets remainder
                        end_idx = len(sentences)
                    else:
                        end_idx = (i + 1) * chunk_size
                    step_text = '. '.join(sentences[start_idx:end_idx]).strip()
                    if step_text:
                        steps.append(step_text)

        # Ensure we have exactly 3 steps, filling with generic advice if needed
        while len(steps) < 3:
            steps.append("Continue practicing with questions at your current ability level to build confidence and reinforce concepts.")

        return steps[:3]  # Return only first 3 steps

    def _generate_fallback_plan(self, user_performance_data):
        """
        Generate a basic study plan if Gemini API fails
        """
        weak_topics = user_performance_data.get("weak_topics", [])
        final_ability_score = user_performance_data.get("final_ability_score", 0.5)

        if weak_topics:
            focus_topic = weak_topics[0]  # Focus on first weak topic
        else:
            focus_topic = "general concepts"

        # Determine difficulty level based on final ability score
        if final_ability_score < 0.4:
            level = "beginner"
            strategy = "focus on foundational concepts"
        elif final_ability_score < 0.7:
            level = "intermediate"
            strategy = "practice mixed difficulty problems"
        else:
            level = "advanced"
            strategy = "challenge yourself with harder problems"

        fallback_steps = [
            f"Focus intensively on {focus_topic} through targeted practice problems.",
            f"Review fundamental concepts at {level} level to {strategy}.",
            "Take timed practice tests to build confidence and improve pacing."
        ]

        return {
            "study_plan": fallback_steps,
            "raw_response": "Fallback study plan generated due to API limitations",
            "analysis": {
                "overall_accuracy": user_performance_data.get("overall_accuracy", 0),
                "weak_topics": weak_topics,
                "final_ability_score": final_ability_score,
                "topics_reviewed": user_performance_data.get("topics_reviewed", [])
            }
        }


# Test the AI Insights Generator
if __name__ == "__main__":
    # Example usage
    try:
        ai_generator = AIInsightsGenerator()

        # Sample performance data (this would come from the database)
        sample_data = {
            "overall_accuracy": 0.65,
            "weak_topics": ["Algebra", "Probability"],
            "final_ability_score": 0.55,
            "topics_reviewed": ["Algebra", "Geometry", "Arithmetic", "Vocabulary", "Probability"]
        }

        print("Generating sample study plan...")
        result = ai_generator.generate_study_plan(sample_data)

        print("\n=== GENERATED STUDY PLAN ===")
        for i, step in enumerate(result["study_plan"], 1):
            print(f"\nSTEP {i}: {step}")

        print(f"\nAnalysis: {result['analysis']}")

    except ValueError as e:
        print(f"Error: {e}")
        print("Make sure to set your GEMINI_API_KEY in the .env file")
    except Exception as e:
        print(f"Unexpected error: {e}")
