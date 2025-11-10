from utils.logger import setup_logger

logger = setup_logger(__name__)

class ProblemService:
    """문제 조회 및 관리 서비스"""
    
    def __init__(self, db):
        self.db = db
    
    def get_test_problems(self, difficulty='Easy', limit=20):
        """
        난이도별 테스트 문제 조회
        
        Args:
            difficulty: 난이도 ('Easy', 'Medium', 'Hard')
            limit: 문제 개수
            
        Returns:
            list: 문제 리스트
        """
        try:
            logger.info(f"문제 조회 시작 - 난이도: {difficulty}, 개수: {limit}")
            
            problems_ref = self.db.collection('problems')\
                .where('difficulty', '==', difficulty)\
                .limit(limit)
            
            docs = problems_ref.stream()
            
            problems_list = []
            for doc in docs:
                problem_data = doc.to_dict()
                if problem_data:
                    problem_data['id'] = doc.id
                    problems_list.append(problem_data)
            
            logger.info(f"문제 {len(problems_list)}개 조회 완료")
            return problems_list
            
        except Exception as e:
            logger.error(f"문제 조회 실패: {e}", exc_info=True)
            raise
    
    def get_problems_by_ids(self, problem_ids):
        """
        ID 리스트로 문제 상세 정보 조회
        
        Args:
            problem_ids: 문제 ID 리스트
            
        Returns:
            dict: {problem_id: problem_data}
        """
        try:
            logger.info(f"{len(problem_ids)}개 문제 상세 정보 조회 시작")
            
            problem_refs = [
                self.db.collection('problems').document(pid) 
                for pid in problem_ids
            ]
            
            problem_docs = self.db.get_all(problem_refs)
            
            problems = {}
            for doc in problem_docs:
                if doc.exists:
                    doc_data = doc.to_dict()
                    if doc_data:
                        problems[doc.id] = {
                            'text': doc_data.get('text_latex'),
                            'correct_answer': doc_data.get('correct_answer'),
                            'solution': doc_data.get('solution_step_by_step'),
                            'category': doc_data.get('curriculum_category'),
                            'explanation': doc_data.get('explanation')  # 캐시된 해설
                        }

            logger.info(f"{len(problems)}개 문제 정보 조회 완료")
            return problems

        except Exception as e:
            logger.error(f"문제 정보 조회 실패: {e}", exc_info=True)
            raise

    def get_explanation(self, problem_id):
        """
        캐시된 해설 조회

        Args:
            problem_id: 문제 ID

        Returns:
            str or None: 캐시된 해설 또는 None
        """
        try:
            doc_ref = self.db.collection('problems').document(problem_id)
            doc = doc_ref.get()

            if doc.exists:
                data = doc.to_dict()
                explanation = data.get('explanation')
                if explanation:
                    logger.info(f"문제 {problem_id} 캐시된 해설 조회 성공")
                    return explanation

            logger.info(f"문제 {problem_id} 캐시된 해설 없음")
            return None

        except Exception as e:
            logger.error(f"해설 조회 실패: {e}", exc_info=True)
            return None

    def cache_explanation(self, problem_id, explanation):
        """
        AI 생성 해설을 데이터베이스에 캐싱

        Args:
            problem_id: 문제 ID
            explanation: AI 생성 해설

        Returns:
            bool: 성공 여부
        """
        try:
            doc_ref = self.db.collection('problems').document(problem_id)
            doc_ref.update({
                'explanation': explanation,
                'explanation_generated_at': self.db.SERVER_TIMESTAMP
            })
            logger.info(f"문제 {problem_id} 해설 캐싱 성공")
            return True

        except Exception as e:
            logger.error(f"해설 캐싱 실패 (문제 ID: {problem_id}): {e}", exc_info=True)
            return False