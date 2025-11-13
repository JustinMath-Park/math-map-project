"""
커리큘럼 관리 서비스
SAT, IGCSE 등의 공식 커리큘럼 데이터 관리
"""
from utils.firebase_client import initialize_firebase
from utils.logger import setup_logger
from typing import List, Dict, Optional

logger = setup_logger(__name__)


class CurriculumService:
    """커리큘럼 데이터 관리 서비스"""

    def __init__(self):
        """커리큘럼 서비스 초기화"""
        self.db = initialize_firebase()
        self.collection = 'curriculum'

    def get_all_curriculums(self) -> List[Dict]:
        """
        모든 커리큘럼 목록 조회

        Returns:
            커리큘럼 목록 (exam_type, subject, version만 포함)
        """
        try:
            docs = self.db.collection(self.collection).stream()

            curriculums = []
            for doc in docs:
                data = doc.to_dict()
                curriculums.append({
                    'curriculum_id': doc.id,
                    'exam_type': data.get('exam_type'),
                    'subject': data.get('subject'),
                    'version': data.get('version'),
                    'description': data.get('description', '')
                })

            logger.info(f"커리큘럼 목록 조회 성공: {len(curriculums)}개")
            return curriculums

        except Exception as e:
            logger.error(f"커리큘럼 목록 조회 실패: {e}", exc_info=True)
            return []

    def get_curriculum_by_id(self, curriculum_id: str) -> Optional[Dict]:
        """
        특정 커리큘럼 상세 조회

        Args:
            curriculum_id: 커리큘럼 ID (예: SAT-MATH-2024)

        Returns:
            커리큘럼 전체 데이터 (domains, topics 포함)
        """
        try:
            doc = self.db.collection(self.collection).document(curriculum_id).get()

            if not doc.exists:
                logger.warning(f"커리큘럼을 찾을 수 없음: {curriculum_id}")
                return None

            data = doc.to_dict()
            data['curriculum_id'] = doc.id

            logger.info(f"커리큘럼 조회 성공: {curriculum_id}")
            return data

        except Exception as e:
            logger.error(f"커리큘럼 조회 실패: {e}", exc_info=True)
            return None

    def get_curriculums_by_exam_type(self, exam_type: str) -> List[Dict]:
        """
        시험 유형별 커리큘럼 조회

        Args:
            exam_type: 시험 유형 (SAT, IGCSE, etc.)

        Returns:
            해당 시험 유형의 커리큘럼 목록
        """
        try:
            docs = self.db.collection(self.collection)\
                .where('exam_type', '==', exam_type)\
                .stream()

            curriculums = []
            for doc in docs:
                data = doc.to_dict()
                data['curriculum_id'] = doc.id
                curriculums.append(data)

            logger.info(f"{exam_type} 커리큘럼 조회 성공: {len(curriculums)}개")
            return curriculums

        except Exception as e:
            logger.error(f"{exam_type} 커리큘럼 조회 실패: {e}", exc_info=True)
            return []

    def create_or_update_curriculum(self, curriculum_id: str, curriculum_data: Dict) -> bool:
        """
        커리큘럼 생성 또는 업데이트

        Args:
            curriculum_id: 커리큘럼 ID
            curriculum_data: 커리큘럼 데이터

        Returns:
            성공 여부
        """
        try:
            self.db.collection(self.collection).document(curriculum_id).set(curriculum_data)
            logger.info(f"커리큘럼 저장 성공: {curriculum_id}")
            return True

        except Exception as e:
            logger.error(f"커리큘럼 저장 실패: {e}", exc_info=True)
            return False
