from typing import Dict, Any
from firebase_admin import firestore
from .question_service import QuestionService

class AdaptiveTestService:
    def __init__(self, db):
        self.db = db
        self.question_service = QuestionService(db)
        self.TOTAL_QUESTIONS = 3

    def start_test(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initializes a new test session.
        """
        session_data = {
            'user_context': user_context,
            'current_question_index': 0,
            'answers': [],
            'current_difficulty': 'Medium',
            'created_at': firestore.SERVER_TIMESTAMP,
            'is_finished': False
        }
        
        # Create session in DB
        doc_ref = self.db.collection('test_sessions').document()
        doc_ref.set(session_data)
        
        # Get first question
        first_question = self.question_service.get_question(
            curriculum_system=user_context['system'],
            grade=user_context['grade'],
            difficulty='Medium'
        )
        
        return {
            'session_id': doc_ref.id,
            'total_questions': self.TOTAL_QUESTIONS,
            'first_question': self._sanitize_question(first_question)
        }

    def submit_answer(self, session_id: str, question_id: str, answer: str) -> Dict[str, Any]:
        """
        Processes an answer and determines the next step.
        """
        session_ref = self.db.collection('test_sessions').document(session_id)
        session = session_ref.get().to_dict()
        
        if not session:
            raise ValueError("Session not found")
            
        # Verify answer (In a real app, fetch question from DB to check correct_answer)
        # For prototype, we assume we can get the question details or they were stored in session
        # Optimization: Store current question ID and correct answer in session during 'get_question'
        
        # 1. Fetch question to check answer
        question_doc = self.db.collection('questions').document(question_id).get()
        question_data = question_doc.to_dict()
        is_correct = (question_data['correct_answer'] == answer)
        
        # 2. Update Session
        new_answer_record = {
            'question_id': question_id,
            'user_answer': answer,
            'is_correct': is_correct,
            'difficulty': question_data['difficulty'],
            'topic': question_data.get('topic')
        }
        
        session['answers'].append(new_answer_record)
        session['current_question_index'] += 1
        
        # 3. Check if finished
        if session['current_question_index'] >= self.TOTAL_QUESTIONS:
            session['is_finished'] = True
            session_ref.set(session)
            return {
                'is_finished': True,
                'results': self._calculate_results(session)
            }
            
        # 4. Adaptive Logic: Determine next difficulty
        next_difficulty = self._calculate_next_difficulty(session['current_difficulty'], is_correct)
        session['current_difficulty'] = next_difficulty
        session_ref.set(session)
        
        # 5. Get Next Question
        answered_ids = [a['question_id'] for a in session.get('answers', [])]
        
        next_question = self.question_service.get_question(
            curriculum_system=session['user_context']['system'],
            grade=session['user_context']['grade'],
            difficulty=next_difficulty,
            exclude_ids=answered_ids
            # Logic for topic progression can be added here
        )
        
        return {
            'is_finished': False,
            'next_question': self._sanitize_question(next_question)
        }

    def _calculate_next_difficulty(self, current_difficulty: str, is_correct: bool) -> str:
        levels = ['Easy', 'Medium', 'Hard']
        try:
            idx = levels.index(current_difficulty)
        except ValueError:
            idx = 1 # Default Medium
            
        if is_correct:
            return levels[min(idx + 1, len(levels) - 1)]
        else:
            return levels[max(idx - 1, 0)]

    def _calculate_results(self, session: Dict[str, Any]) -> Dict[str, Any]:
        # Simple result logic for prototype
        correct_count = sum(1 for a in session['answers'] if a['is_correct'])
        score_percent = (correct_count / self.TOTAL_QUESTIONS) * 100
        
        rec_text = "You have a solid foundation."
        if score_percent < 50:
            rec_text = "We recommend reviewing earlier concepts."
        elif score_percent > 80:
            rec_text = "You are ready for advanced challenges!"
            
        # Detailed Analysis
        answer_history = []
        topic_stats = {}
        
        for ans in session['answers']:
            # Fetch full question data to get explanation
            q_doc = self.db.collection('questions').document(ans['question_id']).get()
            q_data = q_doc.to_dict() if q_doc.exists else {}
            
            explanation = q_data.get('explanation')
            
            # If incorrect and explanation missing, generate it
            if not ans['is_correct'] and not explanation and q_data:
                explanation = self.question_service.generate_explanation(
                    q_data.get('text_latex', ''),
                    q_data.get('correct_answer', ''),
                    q_data.get('choices', [])
                )
                # Save back to DB
                self.db.collection('questions').document(ans['question_id']).update({'explanation': explanation})
            
            answer_history.append({
                'question_id': ans['question_id'],
                'is_correct': ans['is_correct'],
                'difficulty': ans.get('difficulty', 'Medium'),
                'topic': ans.get('topic', 'General'),
                'explanation': explanation, # Add explanation
                'text_latex': q_data.get('text_latex', 'Question text unavailable') # Add text for context
            })
            
            # Topic Stats
            topic = ans.get('topic', 'General')
            if topic not in topic_stats:
                topic_stats[topic] = {'total': 0, 'correct': 0}
            topic_stats[topic]['total'] += 1
            if ans['is_correct']:
                topic_stats[topic]['correct'] += 1
                
        # Format Topic Analysis
        topic_analysis = []
        for topic, stats in topic_stats.items():
            accuracy = int((stats['correct'] / stats['total']) * 100)
            topic_analysis.append({
                'topic': topic,
                'accuracy': accuracy,
                'total': stats['total']
            })

        # Generate AI Performance Summary
        summary_stats = {
            'grade': session['user_context']['grade'],
            'score': correct_count,
            'total': self.TOTAL_QUESTIONS,
            'topic_analysis': topic_analysis,
            'final_difficulty': session.get('current_difficulty', 'Medium')
        }
        ai_recommendation = self.question_service.generate_performance_summary(summary_stats)

        return {
            'score': correct_count,
            'total': self.TOTAL_QUESTIONS,
            'score_percent': int(score_percent),
            'recommendation_text': ai_recommendation, # Use AI summary
            'recommended_course': f"{session['user_context']['system']} Math",
            'recommended_module': "Personalized Module",
            'answer_history': answer_history,
            'topic_analysis': topic_analysis
        }

    def _sanitize_question(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Removes the correct answer before sending to frontend."""
        q = question.copy()
        if 'correct_answer' in q:
            del q['correct_answer']
        if 'explanation' in q:
            del q['explanation']
        if 'created_at' in q:
            del q['created_at']
        return q
