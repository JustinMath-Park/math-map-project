"""
사용자 관리 서비스
"""
from google.cloud import firestore
from firebase_admin import auth
from utils.logger import setup_logger
import uuid

logger = setup_logger(__name__)


class UserService:
    """Wix-Firebase 사용자 관리 서비스"""

    def __init__(self, db):
        self.db = db

    def sync_wix_user(self, wix_user_id, email, event_type='login'):
        """
        Wix 사용자를 Firebase와 동기화

        Args:
            wix_user_id: Wix 회원 ID
            email: 이메일
            event_type: 'login', 'created', 'updated', 'deleted'

        Returns:
            dict: {'firebase_uid': str, 'status': str}
        """
        try:
            firebase_uid = f"wix_{wix_user_id}"

            # 1. Firebase Auth 사용자 확인/생성
            try:
                # 사용자 생성 시도
                user = auth.create_user(
                    uid=firebase_uid,
                    email=email,
                    email_verified=True  # Wix에서 이미 인증됨
                )
                logger.info(f"✓ 새 Firebase 사용자 생성: {firebase_uid}")

            except auth.UidAlreadyExistsError:
                # 이미 존재하면 정보 업데이트
                logger.info(f"기존 Firebase 사용자 발견: {firebase_uid}")
                try:
                    user = auth.update_user(
                        firebase_uid,
                        email=email,
                        email_verified=True
                    )
                    logger.info(f"이메일 업데이트: {firebase_uid}")
                except Exception as update_error:
                    logger.warning(f"사용자 업데이트 실패 (무시): {update_error}")
                    # 업데이트 실패해도 계속 진행

            # 2. Firestore에 사용자 정보 저장/업데이트
            user_data = {
                'wix_user_id': wix_user_id,
                'email': email,
                'sync_status': 'synced',
                'last_synced': firestore.SERVER_TIMESTAMP
            }

            if event_type == 'created':
                user_data['created_at'] = firestore.SERVER_TIMESTAMP

            self.db.collection('users').document(firebase_uid).set(
                user_data,
                merge=True
            )

            logger.info(f"✓ Firestore 동기화 완료: {firebase_uid} (이벤트: {event_type})")

            return {
                'firebase_uid': firebase_uid,
                'status': 'synced'
            }

        except Exception as e:
            logger.error(f"사용자 동기화 실패 - Wix ID: {wix_user_id}, 오류: {e}", exc_info=True)
            raise

    def delete_wix_user(self, wix_user_id):
        """
        Wix 사용자 탈퇴 처리

        Args:
            wix_user_id: Wix 회원 ID

        Returns:
            bool: 성공 여부
        """
        try:
            firebase_uid = f"wix_{wix_user_id}"

            # Firebase Auth 사용자 삭제 (선택사항)
            try:
                auth.delete_user(firebase_uid)
                logger.info(f"Firebase 사용자 삭제: {firebase_uid}")
            except auth.UserNotFoundError:
                logger.warning(f"삭제할 Firebase 사용자 없음: {firebase_uid}")

            # Firestore 정보는 보존 (데이터 분석용) - 상태만 변경
            self.db.collection('users').document(firebase_uid).set({
                'sync_status': 'deleted',
                'deleted_at': firestore.SERVER_TIMESTAMP
            }, merge=True)

            logger.info(f"✓ 회원 탈퇴 처리 완료: {firebase_uid}")
            return True

        except Exception as e:
            logger.error(f"회원 탈퇴 처리 실패 - Wix ID: {wix_user_id}, 오류: {e}", exc_info=True)
            return False

    def create_firebase_custom_token(self, wix_user_id, email):
        """
        Firebase Custom Token 생성 (Firebase Auth 사용자 자동 생성)

        Args:
            wix_user_id: Wix 회원 ID
            email: 이메일

        Returns:
            str: Custom Token
        """
        try:
            firebase_uid = f"wix_{wix_user_id}"

            # 1. Firebase Auth 사용자 확인/생성
            try:
                # 기존 사용자 확인
                auth.get_user(firebase_uid)
                logger.info(f"기존 Firebase Auth 사용자 발견: {firebase_uid}")
            except auth.UserNotFoundError:
                # 사용자가 없으면 생성
                auth.create_user(
                    uid=firebase_uid,
                    email=email,
                    email_verified=True  # Wix에서 이미 인증됨
                )
                logger.info(f"✓ 새 Firebase Auth 사용자 생성: {firebase_uid}")

            # 2. Firestore에 사용자 정보 저장
            user_data = {
                'wix_user_id': wix_user_id,
                'email': email,
                'sync_status': 'synced',
                'last_synced': firestore.SERVER_TIMESTAMP
            }

            # 첫 생성인지 확인
            user_doc = self.db.collection('users').document(firebase_uid).get()
            if not user_doc.exists:
                user_data['created_at'] = firestore.SERVER_TIMESTAMP

            self.db.collection('users').document(firebase_uid).set(
                user_data,
                merge=True
            )
            logger.info(f"✓ Firestore 동기화 완료: {firebase_uid}")

            # 3. Custom Token 생성
            custom_token = auth.create_custom_token(
                firebase_uid,
                developer_claims={'email': email}
            )

            logger.info(f"✓ Custom Token 생성 성공: {firebase_uid}")

            return custom_token.decode('utf-8')

        except Exception as e:
            logger.error(f"Custom Token 생성 실패 - Wix ID: {wix_user_id}, 오류: {e}", exc_info=True)
            raise

    def get_user_profile(self, user_id):
        """
        사용자 프로필 조회

        Args:
            user_id: Firebase UID

        Returns:
            dict: 사용자 프로필 정보
        """
        try:
            user_doc = self.db.collection('users').document(user_id).get()

            if not user_doc.exists:
                logger.warning(f"사용자를 찾을 수 없습니다: {user_id}")
                return None

            user_data = user_doc.to_dict()

            return {
                'wix_user_id': user_data.get('wix_user_id'),
                'email': user_data.get('email'),
                'profile': user_data.get('profile', {}),
                'sync_status': user_data.get('sync_status'),
                'created_at': user_data.get('created_at'),
                'last_synced': user_data.get('last_synced')
            }

        except Exception as e:
            logger.error(f"프로필 조회 실패 - User ID: {user_id}, 오류: {e}", exc_info=True)
            return None

    def save_user_profile(self, user_id, grade, curriculum_category, target_level='Medium'):
        """
        사용자 학습 프로필 저장

        Args:
            user_id: Firebase UID
            grade: 학년
            curriculum_category: 커리큘럼 카테고리
            target_level: 목표 난이도

        Returns:
            bool: 성공 여부
        """
        try:
            self.db.collection('users').document(user_id).set({
                'profile': {
                    'grade': grade,
                    'curriculum_category': curriculum_category,
                    'target_level': target_level,
                    'updated_at': firestore.SERVER_TIMESTAMP
                }
            }, merge=True)

            logger.info(f"✓ 프로필 저장 완료 - User ID: {user_id}")
            return True

        except Exception as e:
            logger.error(f"프로필 저장 실패 - User ID: {user_id}, 오류: {e}", exc_info=True)
            return False

    def save_test_result(self, user_id, results, analysis_report, time_info):
        """
        테스트 결과 저장

        Args:
            user_id: Firebase UID
            results: 문제별 채점 결과
            analysis_report: AI 분석 리포트
            time_info: 시간 정보

        Returns:
            str: test_session_id
        """
        try:
            # 약점/강점 카테고리 추출
            weak_categories = []
            strong_categories = []
            correct_count = 0

            for result in results:
                category = result.get('category', 'Unknown')
                if result['is_correct']:
                    correct_count += 1
                    if category not in strong_categories:
                        strong_categories.append(category)
                else:
                    if category not in weak_categories:
                        weak_categories.append(category)

            # 테스트 세션 ID 생성
            test_session_id = str(uuid.uuid4())

            # Firestore에 저장
            test_history_ref = self.db.collection('users')\
                .document(user_id)\
                .collection('test_history')\
                .document(test_session_id)

            test_history_ref.set({
                'test_date': firestore.SERVER_TIMESTAMP,
                'time_spent': time_info.get('total_time_spent', 0),
                'is_overtime': time_info.get('is_overtime', False),
                'problems': [r['id'] for r in results],
                'answers': {r['id']: r.get('user_answer', '') for r in results},
                'results': {r['id']: r['is_correct'] for r in results},
                'score': (correct_count / len(results)) * 100 if results else 0,
                'weak_categories': weak_categories,
                'strong_categories': strong_categories,
                'ai_analysis': analysis_report
            })

            logger.info(f"✓ 테스트 결과 저장 완료 - User: {user_id}, Session: {test_session_id}")

            return test_session_id

        except Exception as e:
            logger.error(f"테스트 결과 저장 실패 - User ID: {user_id}, 오류: {e}", exc_info=True)
            return None

    def create_test_session(self, user_id, test_type='level_test', grade=None,
                           curriculum_category=None, target_difficulty='Medium',
                           time_limit=600, num_problems=10):
        """
        새로운 테스트 세션 생성 (계층적 구조)

        Args:
            user_id: Firebase UID
            test_type: 테스트 유형 ('level_test', 'practice', 'homework', 'quiz')
            grade: 학년
            curriculum_category: 커리큘럼 카테고리
            target_difficulty: 목표 난이도
            time_limit: 제한 시간 (초)

        Returns:
            str: session_id
        """
        try:
            session_id = str(uuid.uuid4())

            # 세션 데이터
            session_data = {
                'session_id': session_id,
                'user_id': user_id,
                'test_type': test_type,
                'test_date': firestore.SERVER_TIMESTAMP,
                'grade': grade,
                'curriculum_category': curriculum_category,
                'target_difficulty': target_difficulty,
                'time_limit': time_limit,
                'num_problems': num_problems,
                'total_problems': 0,
                'correct_count': 0,
                'score': 0.0,
                'time_spent': 0,
                'is_overtime': False,
                'is_completed': False,
                'is_analyzed': False,
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            }

            # Firestore에 저장
            session_ref = self.db.collection('users')\
                .document(user_id)\
                .collection('test_sessions')\
                .document(session_id)

            session_ref.set(session_data)

            logger.info(f"✓ 테스트 세션 생성 완료 - User: {user_id}, Session: {session_id}")

            return session_id

        except Exception as e:
            logger.error(f"테스트 세션 생성 실패 - User ID: {user_id}, 오류: {e}", exc_info=True)
            return None

    def save_answer(self, user_id, session_id, problem_id, user_answer,
                   correct_answer, is_correct, problem_data, time_spent=0):
        """
        문제별 답변 저장

        Args:
            user_id: Firebase UID
            session_id: 테스트 세션 ID
            problem_id: 문제 ID
            user_answer: 학생 답변
            correct_answer: 정답
            is_correct: 정답 여부
            problem_data: 문제 메타데이터 (category, difficulty 등)
            time_spent: 소요 시간 (초)

        Returns:
            bool: 성공 여부
        """
        try:
            answer_data = {
                'problem_id': problem_id,
                'problem_category': problem_data.get('category', 'Unknown'),
                'problem_subcategory': problem_data.get('subcategory', ''),
                'problem_difficulty': problem_data.get('difficulty', 'Medium'),
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'time_spent': time_spent,
                'answered_at': firestore.SERVER_TIMESTAMP,
                'needs_review': not is_correct,
                'is_flagged': False
            }

            # Firestore에 저장
            answer_ref = self.db.collection('users')\
                .document(user_id)\
                .collection('test_sessions')\
                .document(session_id)\
                .collection('answers')\
                .document(problem_id)

            answer_ref.set(answer_data)

            return True

        except Exception as e:
            logger.error(f"답변 저장 실패 - Session: {session_id}, Problem: {problem_id}, 오류: {e}", exc_info=True)
            return False

    def complete_test_session(self, user_id, session_id, results, analysis_report, time_info):
        """
        테스트 세션 완료 및 AI 분석 결과 저장

        Args:
            user_id: Firebase UID
            session_id: 테스트 세션 ID
            results: 문제별 채점 결과 리스트
            analysis_report: AI 분석 리포트
            time_info: 시간 정보

        Returns:
            bool: 성공 여부
        """
        try:
            # 약점/강점 카테고리 추출
            weak_categories = []
            strong_categories = []
            correct_count = 0
            category_stats = {}

            for result in results:
                category = result.get('category', 'Unknown')

                if result['is_correct']:
                    correct_count += 1
                    if category not in strong_categories:
                        strong_categories.append(category)
                else:
                    if category not in weak_categories:
                        weak_categories.append(category)

                # 카테고리별 통계
                if category not in category_stats:
                    category_stats[category] = {'total': 0, 'correct': 0}
                category_stats[category]['total'] += 1
                if result['is_correct']:
                    category_stats[category]['correct'] += 1

            # 세션 업데이트
            session_ref = self.db.collection('users')\
                .document(user_id)\
                .collection('test_sessions')\
                .document(session_id)

            total_problems = len(results)
            score = (correct_count / total_problems * 100) if total_problems > 0 else 0

            session_ref.update({
                'total_problems': total_problems,
                'correct_count': correct_count,
                'score': score,
                'time_spent': time_info.get('total_time_spent', 0),
                'is_overtime': time_info.get('is_overtime', False),
                'weak_categories': weak_categories,
                'strong_categories': strong_categories,
                'ai_summary': analysis_report,
                'is_completed': True,
                'is_analyzed': True,
                'updated_at': firestore.SERVER_TIMESTAMP
            })

            logger.info(f"✓ 테스트 세션 완료 - User: {user_id}, Session: {session_id}, Score: {score:.1f}%")

            # 사용자 통계 업데이트
            self.update_user_stats(user_id, results, score)

            return True

        except Exception as e:
            logger.error(f"테스트 세션 완료 실패 - Session: {session_id}, 오류: {e}", exc_info=True)
            return False

    def update_user_stats(self, user_id, results, new_score):
        """
        사용자 전체 통계 업데이트

        Args:
            user_id: Firebase UID
            results: 문제별 채점 결과
            new_score: 새로운 점수

        Returns:
            bool: 성공 여부
        """
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()

            if not user_doc.exists:
                logger.warning(f"사용자 문서 없음: {user_id}")
                return False

            user_data = user_doc.to_dict()
            stats = user_data.get('stats', {})

            # 전체 통계 업데이트
            total_tests = stats.get('total_tests', 0) + 1
            total_problems = stats.get('total_problems_solved', 0) + len(results)
            total_correct = stats.get('total_correct', 0) + sum(1 for r in results if r['is_correct'])

            # 카테고리별 통계
            category_stats = stats.get('category_stats', {})
            difficulty_stats = stats.get('difficulty_stats', {})

            for result in results:
                category = result.get('category', 'Unknown')
                difficulty = result.get('difficulty', 'Medium')

                # 카테고리별
                if category not in category_stats:
                    category_stats[category] = {'total': 0, 'correct': 0, 'accuracy': 0.0}
                category_stats[category]['total'] += 1
                if result['is_correct']:
                    category_stats[category]['correct'] += 1
                category_stats[category]['accuracy'] = (
                    category_stats[category]['correct'] / category_stats[category]['total']
                )

                # 난이도별
                if difficulty not in difficulty_stats:
                    difficulty_stats[difficulty] = {'total': 0, 'correct': 0, 'accuracy': 0.0}
                difficulty_stats[difficulty]['total'] += 1
                if result['is_correct']:
                    difficulty_stats[difficulty]['correct'] += 1
                difficulty_stats[difficulty]['accuracy'] = (
                    difficulty_stats[difficulty]['correct'] / difficulty_stats[difficulty]['total']
                )

            # 최근 점수 추이
            recent_scores = stats.get('recent_scores', [])
            recent_scores.append(new_score)
            if len(recent_scores) > 5:
                recent_scores = recent_scores[-5:]  # 최근 5개만 유지

            avg_score = sum(recent_scores) / len(recent_scores) if recent_scores else 0

            # 약점/강점 분류 (정확도 기준)
            weak_categories = [cat for cat, data in category_stats.items() if data['accuracy'] < 0.7]
            strong_categories = [cat for cat, data in category_stats.items() if data['accuracy'] >= 0.8]

            # 업데이트
            user_ref.update({
                'stats': {
                    'total_tests': total_tests,
                    'total_problems_solved': total_problems,
                    'total_correct': total_correct,
                    'overall_accuracy': total_correct / total_problems if total_problems > 0 else 0,
                    'category_stats': category_stats,
                    'difficulty_stats': difficulty_stats,
                    'recent_scores': recent_scores,
                    'avg_score_last_5': avg_score,
                    'weak_categories': weak_categories,
                    'strong_categories': strong_categories,
                    'last_updated': firestore.SERVER_TIMESTAMP
                }
            })

            logger.info(f"✓ 사용자 통계 업데이트 완료 - User: {user_id}")

            return True

        except Exception as e:
            logger.error(f"사용자 통계 업데이트 실패 - User ID: {user_id}, 오류: {e}", exc_info=True)
            return False
