import json
import time
from typing import List, Optional, Dict, Any
from firebase_admin import firestore
from google.cloud import aiplatform
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models
from config import Config

class QuestionService:
    def __init__(self, db):
        self.db = db
        self.model = GenerativeModel(Config.MODEL_FLASH)

    def get_question(self, curriculum_system: str, grade: str, topic: Optional[str] = None, difficulty: str = "Medium", exclude_ids: List[str] = []) -> Dict[str, Any]:
        """
        Retrieves a question from Firestore or generates one if not found.
        Avoids returning questions in exclude_ids.
        """
        import random

        # 1. Try to find an existing question in DB
        questions_ref = self.db.collection('questions')
        query = questions_ref.where('curriculum_system', '==', curriculum_system)\
                             .where('grade', '==', grade)\
                             .where('difficulty', '==', difficulty)
        
        if topic:
            query = query.where('topic', '==', topic)
            
        # Get a batch of questions to pick randomly
        # Limit increased to allow filtering
        docs = query.limit(20).get()
        
        valid_questions = []
        for doc in docs:
            # Check legacy ID format
            if '_' not in doc.id:
                continue
                
            # Check if excluded
            if doc.id in exclude_ids:
                continue
                
            q_data = doc.to_dict()
            q_data['id'] = doc.id
            valid_questions.append(q_data)
            
        if valid_questions:
            # Return a random question from valid candidates
            return random.choice(valid_questions)
            
        # 2. If not found (or all excluded), generate using AI
        return self.generate_question(curriculum_system, grade, topic, difficulty)

    def generate_question(self, curriculum_system: str, grade: str, topic: Optional[str], difficulty: str) -> Dict[str, Any]:
        """
        Generates a math question using Vertex AI.
        """
        prompt = f"""
        Generate a {difficulty} difficulty math question for {grade} grade {curriculum_system} curriculum.
        Topic: {topic if topic else "General Math for this grade"}
        Difficulty: {difficulty}
        
        Output JSON format ONLY.
        IMPORTANT: 
        1. For LaTeX math, use double backslashes (e.g., \\frac{1}{2} instead of \frac{1}{2}) so it is valid JSON.
        2. Do NOT escape % symbols in normal text (e.g., write '25%', not '25\%'). Only use \% if inside $...$.
        3. Do NOT use LaTeX text formatting commands like \\textit, \\textbf, \\text. Use standard text.
        
        {{
            "text_latex": "Question text with LaTeX math wrapped in $...$",
            "choices": [
                {{"id": "A", "text": "Option A"}},
                {{"id": "B", "text": "Option B"}},
                {{"id": "C", "text": "Option C"}},
                {{"id": "D", "text": "Option D"}}
            ],
            "correct_answer": "A",
            "explanation": "Explanation of the solution",
            "topic": "Specific Topic Name",
            "subtopic": "Specific Subtopic Name"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Clean up markdown code blocks if present
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
                
            question_data = json.loads(text)
            
            # Add metadata
            question_data['curriculum_system'] = curriculum_system
            question_data['grade'] = grade
            question_data['difficulty'] = difficulty
            question_data['created_at'] = firestore.SERVER_TIMESTAMP
            
            # Generate readable Document ID
            # Format: {System}_{Grade}_{Topic}_{Timestamp}
            # Sanitize topic to be safe for ID (remove spaces, special chars)
            safe_topic = "".join(c for c in question_data.get('topic', 'General') if c.isalnum())
            timestamp = int(time.time())
            doc_id = f"{curriculum_system}_{grade}_{safe_topic}_{timestamp}"
            
            # Save to DB with custom ID
            self.db.collection('questions').document(doc_id).set(question_data)
            question_data['id'] = doc_id
            
            return question_data
            
        except Exception as e:
            print(f"Error generating question: {e}")
            # Fallback or re-raise
            raise e

    def generate_explanation(self, question_text: str, correct_answer: str, choices: List[Dict]) -> str:
        """Generates an explanation for a question if missing."""
        prompt = f"""
        Explain the solution for the following math problem step-by-step.
        Question: {question_text}
        Choices: {choices}
        Correct Answer ID: {correct_answer}
        
        Keep the explanation concise and easy to understand for a student.
        Use plain text or standard LaTeX for math.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating explanation: {e}")
            return "Explanation currently unavailable."

    def generate_performance_summary(self, stats: Dict[str, Any]) -> str:
        """Generates a personalized performance summary."""
        prompt = f"""
        Analyze the following student math test performance and write a short, encouraging summary (2-3 sentences).
        Explain WHY the specific level/module is recommended based on their accuracy and difficulty level.
        
        Stats:
        - Grade: {stats.get('grade')}
        - Score: {stats.get('score')}/{stats.get('total')}
        - Topic Accuracy: {stats.get('topic_analysis')}
        - Final Difficulty Reached: {stats.get('final_difficulty')}
        
        Output plain text only.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "You have a solid foundation. Keep practicing to improve further!"

    def submit_answer(self, session_id: str, question_id: str, answer: str) -> Dict[str, Any]:
        """
        Records the user's answer and updates the session.
        """
        # This will be handled by the AdaptiveTestService
        pass
