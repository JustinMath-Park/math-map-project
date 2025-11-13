#!/usr/bin/env python3
"""
커리큘럼 데이터 업로드 스크립트
SAT, IGCSE 커리큘럼 JSON 파일을 Firestore에 업로드
"""
import sys
import os
import json

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.curriculum_service import CurriculumService
from utils.logger import setup_logger

logger = setup_logger(__name__)


def load_json_file(file_path: str) -> dict:
    """JSON 파일 로드"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"파일 로드 성공: {file_path}")
        return data
    except Exception as e:
        logger.error(f"파일 로드 실패 ({file_path}): {e}")
        return None


def upload_curriculum(curriculum_data: dict):
    """커리큘럼 데이터를 Firestore에 업로드"""
    try:
        curriculum_service = CurriculumService()
        curriculum_id = curriculum_data.get('curriculum_id')

        if not curriculum_id:
            logger.error("curriculum_id가 없습니다")
            return False

        success = curriculum_service.create_or_update_curriculum(
            curriculum_id,
            curriculum_data
        )

        if success:
            logger.info(f"✅ 업로드 성공: {curriculum_id}")
            return True
        else:
            logger.error(f"❌ 업로드 실패: {curriculum_id}")
            return False

    except Exception as e:
        logger.error(f"업로드 중 에러: {e}", exc_info=True)
        return False


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("📚 커리큘럼 데이터 업로드 시작")
    print("=" * 60)
    print()

    # 스크립트 디렉토리 기준 경로 설정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')

    # 업로드할 파일 목록
    curriculum_files = [
        {
            'name': 'SAT Math 2024',
            'file': os.path.join(data_dir, 'sat_math_curriculum.json')
        },
        {
            'name': 'IGCSE Math 0580',
            'file': os.path.join(data_dir, 'igcse_math_curriculum.json')
        }
    ]

    # 각 커리큘럼 파일 업로드
    success_count = 0
    fail_count = 0

    for curriculum in curriculum_files:
        print(f"📥 {curriculum['name']} 업로드 중...")

        # JSON 파일 로드
        data = load_json_file(curriculum['file'])
        if not data:
            print(f"   ❌ 파일 로드 실패: {curriculum['file']}")
            fail_count += 1
            continue

        # Firestore에 업로드
        if upload_curriculum(data):
            print(f"   ✅ {curriculum['name']} 업로드 완료")
            success_count += 1
        else:
            print(f"   ❌ {curriculum['name']} 업로드 실패")
            fail_count += 1

        print()

    # 결과 출력
    print("=" * 60)
    print(f"업로드 완료: {success_count}개 성공, {fail_count}개 실패")
    print("=" * 60)
    print()

    if success_count > 0:
        print("🎉 커리큘럼 데이터가 Firestore에 업로드되었습니다!")
        print()
        print("📊 확인 방법:")
        print("   1. Firebase Console에서 Firestore 확인")
        print("   2. API 테스트:")
        print("      curl https://my-mvp-backend-1093137562151.asia-northeast3.run.app/curriculums")
        print()


if __name__ == '__main__':
    main()
