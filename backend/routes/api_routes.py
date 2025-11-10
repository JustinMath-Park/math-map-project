from flask import Blueprint, request, jsonify
from services.problem_service import ProblemService
from services.grading_service import GradingService
from services.ai_service import AIService
from utils.logger import setup_logger

logger = setup_logger(__name__)

def create_api_routes(db, ai_client):
    """API 라우트 블루프린트 생성"""
    
    api_bp = Blueprint('api', __name__)
    
    # 서비스 초기화
    problem_service = ProblemService(db)
    grading_service = GradingService()
    ai_service = AIService(ai_client)
    
    @api_bp.route('/get_test_problems', methods=['GET'])
    def get_test_problems():
        """테스트 문제 조회"""
        try:
            logger.info("GET /get_test_problems 요청 수신")
            
            problems = problem_service.get_test_problems(difficulty='Easy', limit=20)
            
            if not problems:
                return jsonify({'error': '문제를 찾을 수 없습니다.'}), 404
            
            return jsonify(problems), 200
            
        except Exception as e:
            logger.error(f"문제 조회 실패: {e}", exc_info=True)
            return jsonify({'error': f'서버 오류: {str(e)}'}), 500
    
    @api_bp.route('/submit_and_analyze', methods=['POST'])
    def submit_and_analyze():
        """답안 제출 및 AI 분석"""
        try:
            logger.info("POST /submit_and_analyze 요청 수신")

            # 1. 요청 데이터 검증
            data = request.json
            if not data or not isinstance(data, dict):
                return jsonify({'error': '유효하지 않은 요청 형식'}), 400

            answers = data.get('answers', {})

            # 시간 정보 추출
            time_info = {
                'total_time_spent': data.get('total_time_spent'),
                'time_limit': data.get('time_limit'),
                'is_overtime': data.get('is_overtime', False)
            }

            if time_info['total_time_spent'] is not None:
                logger.info(f"시간 정보 수신 - 소요시간: {time_info['total_time_spent']}초, "
                          f"제한시간: {time_info['time_limit']}초, "
                          f"초과여부: {time_info['is_overtime']}")

            # answers 형식 처리
            if isinstance(answers, list):
                processed_answers = {}
                for item in answers:
                    if 'problem_id' in item and 'user_answer' in item:
                        processed_answers[item['problem_id']] = item['user_answer']
                answers = processed_answers
            elif not isinstance(answers, dict):
                answers = {}

            if not answers:
                return jsonify({'error': '제출된 답안이 없습니다.'}), 400

            problem_ids = list(answers.keys())
            logger.info(f"{len(problem_ids)}개 답안 처리 시작")

            # 2. 문제 정보 조회
            problems = problem_service.get_problems_by_ids(problem_ids)

            # 3. 채점
            results, wrong_categories = grading_service.grade_answers(answers, problems)

            # 4. AI 해설 생성 (틀린 문제만, 캐싱 적용)
            for result in results:
                if not result['is_correct']:
                    problem_id = result['id']

                    # 캐시된 해설 확인
                    cached_explanation = problems.get(problem_id, {}).get('explanation')

                    if cached_explanation:
                        logger.info(f"문제 {problem_id} 캐시된 해설 사용")
                        result['ai_solution'] = cached_explanation
                    else:
                        # AI 해설 생성
                        logger.info(f"문제 {problem_id} AI 해설 생성")
                        solution = ai_service.generate_solution(
                            problem_id=problem_id,
                            problem_text=result.get('text_latex', ''),
                            user_answer=result['user_answer'],
                            correct_answer=result['correct_answer'],
                            db_solution=result.get('solution')
                        )
                        result['ai_solution'] = solution

                        # 생성된 해설을 데이터베이스에 캐싱
                        problem_service.cache_explanation(problem_id, solution)

            # 5. AI 약점 분석 (시간 정보 포함)
            analysis_report = ai_service.analyze_weakness(
                wrong_categories,
                time_info if time_info['total_time_spent'] is not None else None
            )

            logger.info("답안 처리 완료")

            return jsonify({
                'test_results': results,
                'ai_analysis_report': analysis_report
            }), 200

        except Exception as e:
            logger.error(f"답안 처리 실패: {e}", exc_info=True)
            return jsonify({'error': f'서버 오류: {str(e)}'}), 500
    
    return api_bp