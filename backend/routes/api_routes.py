from flask import Blueprint, request, jsonify
from google.cloud import firestore
from services.problem_service import ProblemService
from services.grading_service import GradingService
from services.ai_service import AIService
from services.user_service import UserService
from services.curriculum_service import CurriculumService
from middleware.auth_middleware import verify_firebase_token
from utils.logger import setup_logger
import hmac
import hashlib
import os

logger = setup_logger(__name__)

def create_api_routes(db, ai_client):
    """API 라우트 블루프린트 생성"""

    api_bp = Blueprint('api', __name__)

    # 서비스 초기화
    problem_service = ProblemService(db)
    grading_service = GradingService()
    ai_service = AIService(ai_client)
    user_service = UserService(db)
    curriculum_service = CurriculumService()

    # Wix Webhook 시크릿 키 (환경 변수에서 로드)
    WIX_WEBHOOK_SECRET = os.getenv('WIX_WEBHOOK_SECRET', '')
    
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
        """답안 제출 및 AI 분석 (계층적 구조)"""
        try:
            logger.info("POST /submit_and_analyze 요청 수신")

            # 1. 요청 데이터 검증
            data = request.json
            if not data or not isinstance(data, dict):
                return jsonify({'error': '유효하지 않은 요청 형식'}), 400

            # 사용자 ID (필수)
            user_id = data.get('user_id')
            if not user_id:
                return jsonify({'error': '사용자 ID가 필요합니다.'}), 400

            # 게스트 모드 확인
            is_guest = data.get('is_guest', False)

            answers = data.get('answers', {})

            # 테스트 메타데이터
            test_metadata = {
                'test_type': data.get('test_type', 'level_test'),
                'grade': data.get('grade'),
                'curriculum_category': data.get('curriculum_category'),
                'target_difficulty': data.get('target_difficulty', 'Medium')
            }

            # 시간 정보 추출
            time_info = {
                'total_time_spent': data.get('total_time_spent'),
                'time_limit': data.get('time_limit', 600),
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
            logger.info(f"{len(problem_ids)}개 답안 처리 시작 - User: {user_id} (게스트: {is_guest})")

            # 2. 테스트 세션 생성 (게스트가 아닐 때만)
            session_id = None
            if not is_guest:
                session_id = user_service.create_test_session(
                    user_id=user_id,
                    test_type=test_metadata['test_type'],
                    grade=test_metadata['grade'],
                    curriculum_category=test_metadata['curriculum_category'],
                    target_difficulty=test_metadata['target_difficulty'],
                    time_limit=time_info['time_limit']
                )

                if not session_id:
                    return jsonify({'error': '테스트 세션 생성 실패'}), 500

            # 3. 문제 정보 조회
            problems = problem_service.get_problems_by_ids(problem_ids)

            # 4. 채점
            results, wrong_categories = grading_service.grade_answers(answers, problems)

            # 5. 문제별 답변 저장 (게스트가 아닐 때만)
            if not is_guest:
                for result in results:
                    problem_id = result['id']

                    user_service.save_answer(
                        user_id=user_id,
                        session_id=session_id,
                        problem_id=problem_id,
                        user_answer=result.get('user_answer', ''),
                        correct_answer=result['correct_answer'],
                        is_correct=result['is_correct'],
                        problem_data={
                            'category': result.get('category', 'Unknown'),
                            'subcategory': result.get('subcategory', ''),
                            'difficulty': result.get('difficulty', 'Medium')
                        },
                        time_spent=0  # TODO: 개별 문제 시간 추적 구현 시 업데이트
                    )

            # 6. AI 해설 생성 (틀린 문제만, 캐싱 적용)
            for result in results:
                if not result['is_correct']:
                    problem_id = result['id']

                    # 캐시된 해설 확인
                    cached_explanation = problems.get(problem_id, {}).get('explanation')

                    if cached_explanation:
                        logger.info(f"문제 {problem_id} 캐시된 해설 사용")
                        result['ai_solution'] = cached_explanation
                    else:
                        # AI 해설 생성 (일반 해설, user_answer 제외)
                        logger.info(f"문제 {problem_id} AI 해설 생성")
                        solution = ai_service.generate_solution(
                            problem_id=problem_id,
                            problem_text=result.get('text_latex', ''),
                            correct_answer=result['correct_answer'],
                            db_solution=result.get('solution')
                        )
                        result['ai_solution'] = solution

                        # 생성된 해설을 데이터베이스에 캐싱
                        problem_service.cache_explanation(problem_id, solution)

            # 7. AI 약점 분석 (시간 정보 포함)
            analysis_report = ai_service.analyze_weakness(
                wrong_categories,
                time_info if time_info['total_time_spent'] is not None else None
            )

            # 8. 테스트 세션 완료 및 통계 업데이트 (게스트가 아닐 때만)
            if not is_guest:
                user_service.complete_test_session(
                    user_id=user_id,
                    session_id=session_id,
                    results=results,
                    analysis_report=analysis_report,
                    time_info=time_info
                )

                # 9. 기존 test_history에도 저장 (호환성 유지)
                user_service.save_test_result(
                    user_id=user_id,
                    results=results,
                    analysis_report=analysis_report,
                    time_info=time_info
                )

            logger.info(f"답안 처리 완료 - Session: {session_id} (게스트: {is_guest})")

            return jsonify({
                'session_id': session_id,
                'test_results': results,
                'ai_analysis_report': analysis_report
            }), 200

        except Exception as e:
            logger.error(f"답안 처리 실패: {e}", exc_info=True)

            # 에러 타입에 따라 다른 메시지 반환
            error_message = '서버 오류가 발생했습니다.'
            error_type = 'SERVER_ERROR'

            error_str = str(e).lower()
            if 'timeout' in error_str or 'deadline' in error_str:
                error_message = '네트워크 연결이 느립니다. 안정적인 Wi-Fi 환경에서 다시 시도해주세요.'
                error_type = 'NETWORK_TIMEOUT'
            elif 'network' in error_str or 'connection' in error_str:
                error_message = '네트워크 연결에 문제가 있습니다. 인터넷 연결을 확인하고 다시 시도해주세요.'
                error_type = 'NETWORK_ERROR'
            elif 'unavailable' in error_str or 'service' in error_str:
                error_message = '서버에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요.'
                error_type = 'SERVICE_UNAVAILABLE'

            return jsonify({
                'error': error_message,
                'error_type': error_type
            }), 500

    # ==================== 게스트 사용자 API ====================

    @api_bp.route('/register_guest', methods=['POST'])
    def register_guest():
        """
        게스트 사용자 등록

        요청 Body:
        {
            "name": "홍길동",
            "grade": "Grade 7"
        }

        응답:
        {
            "guest_id": "abc123-def456-...",
            "message": "게스트 등록 완료"
        }
        """
        try:
            data = request.json
            name = data.get('name')
            grade = data.get('grade')

            if not name or not grade:
                return jsonify({'error': '필수 필드 누락: name, grade'}), 400

            # Firestore에 게스트 사용자 생성
            guest_ref = db.collection('guest_users').document()
            guest_id = guest_ref.id

            guest_ref.set({
                'name': name,
                'grade': grade,
                'curriculum_category': 'General',
                'target_level': 'Medium',
                'created_at': firestore.SERVER_TIMESTAMP
            })

            logger.info(f"게스트 등록 완료 - Guest ID: {guest_id}")

            return jsonify({
                'guest_id': guest_id,
                'message': '게스트 등록 완료'
            }), 200

        except Exception as e:
            logger.error(f"게스트 등록 실패: {e}", exc_info=True)
            return jsonify({'error': f'서버 오류: {str(e)}'}), 500

    @api_bp.route('/guest/<guest_id>/test_result', methods=['POST'])
    def save_guest_test_result(guest_id):
        """
        게스트 테스트 결과 저장

        요청 Body:
        {
            "results": [...],
            "analysis_report": "...",
            "time_info": {...}
        }
        """
        try:
            data = request.json
            results = data.get('results', [])
            analysis_report = data.get('analysis_report', '')
            time_info = data.get('time_info', {})

            if not results:
                return jsonify({'error': '결과 데이터가 없습니다.'}), 400

            # 게스트 사용자 존재 확인
            guest_ref = db.collection('guest_users').document(guest_id)
            guest_doc = guest_ref.get()

            if not guest_doc.exists:
                return jsonify({'error': '게스트 사용자를 찾을 수 없습니다.'}), 404

            # 테스트 결과 저장 (user_service의 로직 재사용)
            test_session_id = user_service.save_test_result(
                user_id=guest_id,
                results=results,
                analysis_report=analysis_report,
                time_info=time_info
            )

            if test_session_id:
                logger.info(f"게스트 테스트 결과 저장 완료 - Guest: {guest_id}, Session: {test_session_id}")
                return jsonify({
                    'test_session_id': test_session_id,
                    'message': '테스트 결과 저장 완료'
                }), 200
            else:
                return jsonify({'error': '결과 저장 실패'}), 500

        except Exception as e:
            logger.error(f"게스트 테스트 결과 저장 실패: {e}", exc_info=True)
            return jsonify({'error': f'서버 오류: {str(e)}'}), 500

    # ==================== Wix 통합 API ====================

    @api_bp.route('/wix_velo_sync', methods=['POST'])
    def wix_velo_sync():
        """
        Wix Velo Backend Events 동기화 엔드포인트
        (서명 검증 없음 - Velo Backend에서 직접 호출)

        요청 Body:
        {
            "wix_user_id": "abc123",
            "email": "user@example.com",
            "event_type": "created" | "updated" | "login"
        }
        """
        try:
            data = request.json
            wix_user_id = data.get('wix_user_id')
            email = data.get('email')
            event_type = data.get('event_type', 'login')

            if not wix_user_id or not email:
                return jsonify({'error': '필수 필드 누락: wix_user_id, email'}), 400

            # Firebase 동기화
            result = user_service.sync_wix_user(
                wix_user_id=wix_user_id,
                email=email,
                event_type=event_type
            )

            logger.info(f"Velo 동기화 성공 - Firebase UID: {result['firebase_uid']}")
            return jsonify({'status': 'success', 'firebase_uid': result['firebase_uid']}), 200

        except Exception as e:
            logger.error(f"Velo 동기화 실패: {e}", exc_info=True)
            return jsonify({'error': f'서버 오류: {str(e)}'}), 500

    def verify_wix_signature(payload_body, signature_header):
        """Wix Webhook HMAC 서명 검증"""
        if not WIX_WEBHOOK_SECRET:
            logger.warning("WIX_WEBHOOK_SECRET이 설정되지 않았습니다.")
            return False

        expected_signature = hmac.new(
            WIX_WEBHOOK_SECRET.encode('utf-8'),
            payload_body,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected_signature, signature_header)

    @api_bp.route('/wix_webhook', methods=['POST'])
    def wix_webhook():
        """
        Wix Webhook 수신 엔드포인트

        이벤트 타입:
        - Members/Member Created
        - Members/Profile Updated
        - Members/Member Deleted
        """
        try:
            # 1. 서명 검증
            signature = request.headers.get('X-Wix-Webhook-Signature', '')
            payload_body = request.get_data()

            if not verify_wix_signature(payload_body, signature):
                logger.warning("Wix Webhook 서명 검증 실패")
                return jsonify({'error': '서명 검증 실패'}), 401

            # 2. 이벤트 데이터 파싱
            data = request.json
            event_type = data.get('event', '')
            member_data = data.get('data', {})

            logger.info(f"Wix Webhook 수신 - 이벤트: {event_type}")

            # 3. 이벤트별 처리
            if event_type == 'Members/Member Created' or event_type == 'Members/Profile Updated':
                wix_user_id = member_data.get('id')
                email = member_data.get('loginEmail')

                if not wix_user_id or not email:
                    return jsonify({'error': '필수 필드 누락: id, loginEmail'}), 400

                # Firebase 동기화
                result = user_service.sync_wix_user(
                    wix_user_id=wix_user_id,
                    email=email,
                    event_type='created' if event_type == 'Members/Member Created' else 'updated'
                )

                logger.info(f"회원 동기화 성공 - Firebase UID: {result['firebase_uid']}")
                return jsonify({'status': 'success', 'firebase_uid': result['firebase_uid']}), 200

            elif event_type == 'Members/Member Deleted':
                wix_user_id = member_data.get('id')

                if not wix_user_id:
                    return jsonify({'error': '필수 필드 누락: id'}), 400

                # Firebase 탈퇴 처리
                success = user_service.delete_wix_user(wix_user_id)

                if success:
                    logger.info(f"회원 탈퇴 처리 성공 - Wix ID: {wix_user_id}")
                    return jsonify({'status': 'success'}), 200
                else:
                    return jsonify({'error': '탈퇴 처리 실패'}), 500

            else:
                logger.warning(f"처리되지 않은 이벤트 타입: {event_type}")
                return jsonify({'status': 'ignored'}), 200

        except Exception as e:
            logger.error(f"Wix Webhook 처리 실패: {e}", exc_info=True)
            return jsonify({'error': f'서버 오류: {str(e)}'}), 500

    @api_bp.route('/wix_login', methods=['POST'])
    def wix_login():
        """
        Wix 회원 로그인 → Firebase Custom Token 발급

        요청 Body:
        {
            "wix_user_id": "abc123",
            "email": "user@example.com"
        }

        응답:
        {
            "custom_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
            "firebase_uid": "wix_abc123"
        }
        """
        try:
            data = request.json
            wix_user_id = data.get('wix_user_id')
            email = data.get('email')

            if not wix_user_id or not email:
                return jsonify({'error': '필수 필드 누락: wix_user_id, email'}), 400

            # Custom Token 생성
            custom_token = user_service.create_firebase_custom_token(wix_user_id, email)

            logger.info(f"Wix 로그인 성공 - Wix ID: {wix_user_id}")

            return jsonify({
                'custom_token': custom_token,
                'firebase_uid': f'wix_{wix_user_id}'
            }), 200

        except Exception as e:
            logger.error(f"Wix 로그인 실패: {e}", exc_info=True)
            return jsonify({'error': f'로그인 실패: {str(e)}'}), 500

    @api_bp.route('/user/profile', methods=['GET'])
    @verify_firebase_token
    def get_user_profile():
        """
        사용자 프로필 조회 (Firebase Auth 필요)

        요청 Header:
        Authorization: Bearer <firebase_id_token>

        응답:
        {
            "wix_user_id": "abc123",
            "email": "user@example.com",
            "profile": {
                "grade": "Grade 10",
                "curriculum_category": "SAT",
                "target_level": "Medium"
            },
            "sync_status": "synced",
            "created_at": "...",
            "last_synced": "..."
        }
        """
        try:
            user_id = request.user_id  # @verify_firebase_token에서 설정됨

            profile = user_service.get_user_profile(user_id)

            if not profile:
                return jsonify({'error': '사용자를 찾을 수 없습니다.'}), 404

            return jsonify(profile), 200

        except Exception as e:
            logger.error(f"프로필 조회 실패: {e}", exc_info=True)
            return jsonify({'error': f'서버 오류: {str(e)}'}), 500

    @api_bp.route('/user/profile', methods=['POST'])
    @verify_firebase_token
    def save_user_profile():
        """
        사용자 학습 프로필 저장 (Firebase Auth 필요)

        요청 Header:
        Authorization: Bearer <firebase_id_token>

        요청 Body:
        {
            "grade": "Grade 10",
            "curriculum_category": "SAT",
            "target_level": "Medium"
        }
        """
        try:
            user_id = request.user_id
            data = request.json

            grade = data.get('grade')
            curriculum_category = data.get('curriculum_category')
            target_level = data.get('target_level', 'Medium')

            if not grade or not curriculum_category:
                return jsonify({'error': '필수 필드 누락: grade, curriculum_category'}), 400

            success = user_service.save_user_profile(
                user_id=user_id,
                grade=grade,
                curriculum_category=curriculum_category,
                target_level=target_level
            )

            if success:
                logger.info(f"프로필 저장 완료 - User ID: {user_id}")
                return jsonify({'message': '프로필 저장 완료'}), 200
            else:
                return jsonify({'error': '프로필 저장 실패'}), 500

        except Exception as e:
            logger.error(f"프로필 저장 실패: {e}", exc_info=True)
            return jsonify({'error': f'서버 오류: {str(e)}'}), 500

    @api_bp.route('/user/test_result', methods=['POST'])
    @verify_firebase_token
    def save_test_result():
        """
        테스트 결과 저장 (Firebase Auth 필요)

        요청 Header:
        Authorization: Bearer <firebase_id_token>

        요청 Body:
        {
            "results": [...],  # 문제별 채점 결과
            "analysis_report": "...",  # AI 분석 리포트
            "time_info": {
                "total_time_spent": 1200,
                "is_overtime": false
            }
        }

        응답:
        {
            "test_session_id": "uuid-here",
            "message": "테스트 결과 저장 완료"
        }
        """
        try:
            user_id = request.user_id
            data = request.json

            results = data.get('results', [])
            analysis_report = data.get('analysis_report', '')
            time_info = data.get('time_info', {})

            if not results:
                return jsonify({'error': '결과 데이터가 없습니다.'}), 400

            test_session_id = user_service.save_test_result(
                user_id=user_id,
                results=results,
                analysis_report=analysis_report,
                time_info=time_info
            )

            if test_session_id:
                logger.info(f"테스트 결과 저장 완료 - Session: {test_session_id}")
                return jsonify({
                    'test_session_id': test_session_id,
                    'message': '테스트 결과 저장 완료'
                }), 200
            else:
                return jsonify({'error': '결과 저장 실패'}), 500

        except Exception as e:
            logger.error(f"테스트 결과 저장 실패: {e}", exc_info=True)
            return jsonify({'error': f'서버 오류: {str(e)}'}), 500

    # ==================== 커리큘럼 API ====================

    @api_bp.route('/curriculums', methods=['GET'])
    def get_all_curriculums():
        """
        모든 커리큘럼 목록 조회

        응답:
        [
            {
                "curriculum_id": "SAT-MATH-2024",
                "exam_type": "SAT",
                "subject": "Math",
                "version": "2024",
                "description": "SAT Math 2024 커리큘럼"
            },
            ...
        ]
        """
        try:
            curriculums = curriculum_service.get_all_curriculums()
            return jsonify(curriculums), 200
        except Exception as e:
            logger.error(f"커리큘럼 목록 조회 실패: {e}", exc_info=True)
            return jsonify({'error': f'서버 오류: {str(e)}'}), 500

    @api_bp.route('/curriculums/<curriculum_id>', methods=['GET'])
    def get_curriculum_detail(curriculum_id):
        """
        특정 커리큘럼 상세 조회

        URL 파라미터:
            curriculum_id: 커리큘럼 ID (예: SAT-MATH-2024)

        응답:
        {
            "curriculum_id": "SAT-MATH-2024",
            "exam_type": "SAT",
            "subject": "Math",
            "version": "2024",
            "description": "...",
            "domains": [
                {
                    "domain_id": "algebra",
                    "name": "Algebra",
                    "topics": [...]
                }
            ]
        }
        """
        try:
            curriculum = curriculum_service.get_curriculum_by_id(curriculum_id)

            if curriculum:
                return jsonify(curriculum), 200
            else:
                return jsonify({'error': '커리큘럼을 찾을 수 없습니다'}), 404

        except Exception as e:
            logger.error(f"커리큘럼 조회 실패: {e}", exc_info=True)
            return jsonify({'error': f'서버 오류: {str(e)}'}), 500

    @api_bp.route('/curriculums/exam/<exam_type>', methods=['GET'])
    def get_curriculums_by_exam(exam_type):
        """
        시험 유형별 커리큘럼 조회

        URL 파라미터:
            exam_type: 시험 유형 (SAT, IGCSE, etc.)

        응답:
        [
            {
                "curriculum_id": "SAT-MATH-2024",
                "exam_type": "SAT",
                "subject": "Math",
                ...
            },
            ...
        ]
        """
        try:
            curriculums = curriculum_service.get_curriculums_by_exam_type(exam_type)
            return jsonify(curriculums), 200
        except Exception as e:
            logger.error(f"{exam_type} 커리큘럼 조회 실패: {e}", exc_info=True)
            return jsonify({'error': f'서버 오류: {str(e)}'}), 500

    return api_bp