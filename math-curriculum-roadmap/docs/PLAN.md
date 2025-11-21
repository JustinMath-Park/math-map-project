# Curriculum Roadmap Plan

1. 커리큘럼 조사
   - SAT Math (College Board)
   - AP Calculus AB/BC (College Board)
   - IGCSE Mathematics (Cambridge/Edexcel)
   - A-Level Mathematics/Further Mathematics (Cambridge/Edexcel)

2. Firebase 스키마 제안
   - `curriculums` 콜렉션
     - `exam_type`: SAT/AP/IGCSE/ALEVEL
     - `subject`: Math/Calculus 등
     - `version`: 연도/시행처
     - `domains`: 대단원 배열
     - `topics`: 세부 내용

3. 데이터 입력 플로우
   - `scripts/seed_curriculums.py`에서 JSON 불러와 Firestore에 업서트

4. 프론트엔드 레퍼런스
   - brilliant.org 구조/애니메이션 분석 후 컴포넌트 플로우 정의

