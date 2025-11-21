# Mathiter Apps - Firebase Hosting 배포 완료

## 🎉 배포 완료 (2024-11-21)

3개의 독립적인 앱이 성공적으로 Firebase Hosting에 배포되었습니다.

---

## 📱 배포된 앱 목록

### 1. MVP Test (로그인 없이 문제 풀이 테스트)
- **이름**: mathiter-mvp-test
- **URL**: https://mathiter-mvp-test.web.app
- **설명**: 로그인 정보 없이 AI 수학 문제를 테스트할 수 있는 페이지
- **디렉토리**: `apps/mvp-test/`
- **주요 기능**:
  - 로그인 불필요
  - 즉시 문제 풀이 테스트
  - AI 기반 수학 문제 생성

### 2. Level Test (로그인 정보 확인 후 문제 풀이)
- **이름**: mathiter-level-test
- **URL**: https://mathiter-level-test.web.app
- **설명**: Firebase 인증을 통해 로그인 후 레벨 테스트를 진행하는 페이지
- **디렉토리**: `apps/level-test/`
- **주요 기능**:
  - Firebase 인증 연동
  - 사용자별 진행도 추적
  - 커리큘럼 기반 문제 제공

### 3. Curriculum Navigator (커리큘럼 로드맵)
- **이름**: mathiter-curriculum
- **URL**: https://mathiter-curriculum.web.app
- **설명**: SAT, IGCSE, A-Level 등 시험별 수학 커리큘럼 로드맵
- **디렉토리**: `apps/curriculum-navigator/`
- **주요 기능**:
  - 시험별 커리큘럼 시각화
  - 도메인/토픽 탐색
  - 강의 플로우 제공
  - KaTeX 수식 렌더링

---

## 📁 프로젝트 구조

```
projects/
├── apps/
│   ├── mvp-test/              # 1. MVP 테스트 앱
│   │   └── index.html
│   ├── level-test/            # 2. 레벨 테스트 앱
│   │   ├── index.html
│   │   └── js/
│   └── curriculum-navigator/  # 3. 커리큘럼 네비게이터
│       ├── index.html
│       ├── lecture.html
│       ├── app.js
│       ├── lecture.js
│       ├── data/
│       ├── js/
│       └── assets/
├── backend/                   # Flask 백엔드
│   ├── app.py
│   └── routes/
├── firebase.json              # Firebase 멀티사이트 설정
└── .firebaserc               # Firebase 프로젝트 타겟 설정
```

---

## 🔧 Firebase 설정

### firebase.json
3개의 hosting 타겟으로 구성:
- `mvp-test`: apps/mvp-test
- `level-test`: apps/level-test
- `curriculum-navigator`: apps/curriculum-navigator

### .firebaserc
타겟 매핑:
- mvp-test → mathiter-mvp-test
- level-test → mathiter-level-test
- curriculum-navigator → mathiter-curriculum

---

## 🚀 배포 명령어

### 전체 배포
```bash
cd /Users/justinminim4/projects
firebase deploy --only hosting
```

### 개별 앱 배포
```bash
# MVP Test만 배포
firebase deploy --only hosting:mvp-test

# Level Test만 배포
firebase deploy --only hosting:level-test

# Curriculum Navigator만 배포
firebase deploy --only hosting:curriculum-navigator
```

---

## 🔗 URL 요약

| 앱 이름 | 용도 | URL |
|--------|------|-----|
| **MVP Test** | 로그인 없이 문제 테스트 | https://mathiter-mvp-test.web.app |
| **Level Test** | 로그인 후 레벨 테스트 | https://mathiter-level-test.web.app |
| **Curriculum Navigator** | 커리큘럼 로드맵 | https://mathiter-curriculum.web.app |

---

## 🎯 백엔드 API 연결

### Cloud Run 백엔드
- **URL**: https://my-mvp-backend-1093137562151.us-central1.run.app
- **용도**: Level Test 앱의 문제 생성 및 사용자 데이터 관리
- **위치**: `backend/app.py`

### 연결 방법
Level Test 앱에서 백엔드 API를 호출:
```javascript
const API_URL = 'https://my-mvp-backend-1093137562151.us-central1.run.app';
```

---

## ✅ 배포 확인

모든 앱이 정상적으로 배포되었습니다:

1. ✅ MVP Test: "AI Math Level Test" 페이지 로딩
2. ✅ Level Test: "Mathiter - 커리큘럼 브라우저" 페이지 로딩
3. ✅ Curriculum Navigator: "Mathiter Curriculum Roadmap" 페이지 로딩

---

## 📊 Firebase Console

프로젝트 관리: https://console.firebase.google.com/project/my-mvp-backend/overview

### Hosting 섹션에서 확인 가능:
- 각 사이트별 배포 히스토리
- 트래픽 분석
- 도메인 설정
- 롤백 기능

---

## 🔄 업데이트 프로세스

### 1. 파일 수정
해당 앱 디렉토리에서 파일 수정:
```bash
# 예: MVP Test 업데이트
cd apps/mvp-test
# 파일 수정...
```

### 2. 배포
```bash
cd /Users/justinminim4/projects
firebase deploy --only hosting:mvp-test
```

### 3. 확인
브라우저에서 URL 접속하여 변경사항 확인

---

## 🛠 문제 해결

### 배포 실패 시
```bash
# Firebase CLI 재인증
firebase login --reauth

# 프로젝트 확인
firebase projects:list

# 타겟 확인
firebase target:apply hosting mvp-test mathiter-mvp-test
firebase target:apply hosting level-test mathiter-level-test
firebase target:apply hosting curriculum-navigator mathiter-curriculum
```

### 캐시 문제
브라우저에서 Ctrl+Shift+R (강제 새로고침)

---

## 📝 다음 단계

### 추천 작업
1. **커스텀 도메인 연결** (선택)
   - mathiter-mvp.com
   - mathiter-level.com
   - mathiter-curriculum.com

2. **Firestore 연동**
   - 사용자 진행도 저장
   - 문제 풀이 히스토리
   - 학습 통계

3. **Analytics 추가**
   - Google Analytics 4
   - Firebase Analytics
   - 사용자 행동 추적

4. **성능 최적화**
   - 이미지 최적화
   - Code splitting
   - Lazy loading

---

## 🎉 성공!

모든 앱이 성공적으로 배포되었습니다!

각 URL로 접속하여 테스트해보세요:
- https://mathiter-mvp-test.web.app
- https://mathiter-level-test.web.app
- https://mathiter-curriculum.web.app
