from utils.logger import setup_logger

logger = setup_logger(__name__)

class GradingService:
    """답안 채점 서비스"""
    
    @staticmethod
    def grade_answers(user_answers, problems):
        """
        답안 채점
        
        Args:
            user_answers: {problem_id: user_answer}
            problems: {problem_id: problem_data}
            
        Returns:
            tuple: (results, wrong_categories)
        """
        logger.info(f"{len(user_answers)}개 답안 채점 시작")
        
        results = []
        wrong_categories = []
        
        for problem_id, user_answer in user_answers.items():
            problem = problems.get(problem_id, {})
            correct_answer = problem.get('correct_answer')
            
            is_correct = (user_answer == correct_answer) if correct_answer else False
            
            result = {
                'id': problem_id,
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'text_latex': problem.get('text'),
                'solution': problem.get('solution'),
                'category': problem.get('category')
            }
            
            results.append(result)
            
            if not is_correct and problem.get('category'):
                wrong_categories.append(problem.get('category'))
        
        correct_count = sum(1 for r in results if r['is_correct'])
        logger.info(f"채점 완료 - 정답: {correct_count}/{len(results)}")
        
        return results, wrong_categories