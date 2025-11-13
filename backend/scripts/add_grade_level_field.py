"""
문제 은행에 grade_level 필드 추가 스크립트

사용법:
    python3 scripts/add_grade_level_field.py

기능:
    - problems 컬렉션의 모든 문서에 grade_level 배열 필드 추가
    - 난이도(difficulty)에 따라 적절한 학년 범위 자동 설정
    - 이미 grade_level이 있는 문서는 건너뜀
"""

import sys
import os

# 프로젝트 루트를 Python path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.cloud import firestore
from config import Config

# Firebase 인증 설정
if os.path.exists(Config.SERVICE_ACCOUNT_KEY):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Config.SERVICE_ACCOUNT_KEY
    print(f"✓ 서비스 계정 키 파일 설정: {Config.SERVICE_ACCOUNT_KEY}")
else:
    print(f"⚠️  서비스 계정 키 파일을 찾을 수 없습니다: {Config.SERVICE_ACCOUNT_KEY}")
    print("GOOGLE_APPLICATION_CREDENTIALS 환경 변수를 사용합니다.")

def add_grade_level_to_problems():
    """
    기존 problems 컬렉션의 모든 문서에 grade_level 필드 추가
    """
    print("=" * 80)
    print("문제 은행 grade_level 필드 추가 스크립트 시작")
    print("=" * 80)

    # Firestore 클라이언트 초기화
    db = firestore.Client(project=Config.PROJECT_ID)
    problems_ref = db.collection('problems')

    # 모든 문제 조회
    print("\n문제 조회 중...")
    docs = list(problems_ref.stream())
    total_count = len(docs)
    print(f"총 {total_count}개 문제 발견\n")

    updated_count = 0
    skipped_count = 0

    for idx, doc in enumerate(docs, 1):
        problem_data = doc.to_dict()
        problem_id = doc.id

        print(f"[{idx}/{total_count}] 문제 ID: {problem_id}")

        # grade_level 필드가 이미 있는지 확인
        if 'grade_level' in problem_data:
            print(f"  → 이미 grade_level 존재: {problem_data['grade_level']} (건너뜀)\n")
            skipped_count += 1
            continue

        # 난이도별 기본 학년 설정
        difficulty = problem_data.get('difficulty', 'Medium')

        if difficulty == 'Easy':
            default_grade_level = [6, 7, 8, 9]
        elif difficulty == 'Medium':
            default_grade_level = [8, 9, 10, 11]
        elif difficulty == 'Hard':
            default_grade_level = [10, 11, 12]
        else:
            # 난이도 정보가 없거나 알 수 없는 경우 전체 학년
            default_grade_level = [6, 7, 8, 9, 10, 11, 12]

        try:
            # 필드 추가
            doc.reference.update({
                'grade_level': default_grade_level
            })

            updated_count += 1
            print(f"  → 업데이트 완료! grade_level: {default_grade_level} (난이도: {difficulty})\n")

        except Exception as e:
            print(f"  → ⚠️  업데이트 실패: {e}\n")

    print("=" * 80)
    print("스크립트 실행 완료")
    print("=" * 80)
    print(f"총 문제 수: {total_count}")
    print(f"업데이트: {updated_count}개")
    print(f"건너뜀: {skipped_count}개")
    print("=" * 80)


if __name__ == "__main__":
    try:
        add_grade_level_to_problems()
    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
