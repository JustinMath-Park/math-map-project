# 🎓 Mathiter - AI 기반 수학 학습 플랫폼

AI를 활용한 개인 맞춤형 수학 학습 플랫폼입니다. SAT, IGCSE, A-Level 등 다양한 커리큘럼을 지원하며, 학생의 수준에 맞는 문제와 AI 해설을 제공합니다.

[![Firebase Hosting](https://img.shields.io/badge/Firebase-Hosting-orange)](https://firebase.google.com/)
[![Cloud Run](https://img.shields.io/badge/Google%20Cloud-Run-blue)](https://cloud.google.com/run)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-green)](https://flask.palletsprojects.com/)

---

## 🌟 주요 기능

### 1. MVP Test (로그인 없이 바로 테스트)
- 즉시 문제 풀이 시작
- AI 기반 개인 맞춤 해설
- 실시간 채점 및 피드백

👉 **바로 시작**: https://mathiter-mvp-test.web.app

### 2. Level Test (사용자별 레벨 진단)
- Firebase 인증 기반 사용자 관리
- 개인별 학습 진행도 추적
- 커리큘럼 기반 맞춤 문제 제공

👉 **시작하기**: https://mathiter-level-test.web.app

### 3. Curriculum Navigator (학습 로드맵)
- SAT, IGCSE, A-Level 커리큘럼
- 도메인별/토픽별 학습 경로
- KaTeX 기반 수식 렌더링
- 강의 플로우 시스템

👉 **탐색하기**: https://mathiter-curriculum.web.app

---

## 🏗️ 프로젝트 구조

```
math-map-project/
├── apps/                      # 3개의 독립적인 Firebase Hosting 앱
│   ├── mvp-test/             # MVP 테스트 앱
│   ├── level-test/           # 레벨 테스트 앱
│   └── curriculum-navigator/ # 커리큘럼 네비게이터
│
├── backend/                   # Flask 백엔드 (Cloud Run)
│   ├── app.py                # 메인 애플리케이션
│   ├── routes/               # API 엔드포인트
│   ├── services/             # 비즈니스 로직
│   └── utils/                # 유틸리티
│
├── math-curriculum-roadmap/   # 커리큘럼 로드맵 프로젝트
│   ├── frontend/             # 웹 애플리케이션
│   ├── scripts/              # 데이터 시딩 스크립트
│   └── docs/                 # 프로젝트 문서
│
└── 📚 문서/
    ├── HOME_SETUP_GUIDE.md   # 개발 환경 설정 (상세)
    ├── QUICK_START_HOME.md   # 빠른 시작 (5분)
    ├── PROJECT_STATUS.md     # 프로젝트 현재 상태
    └── DEPLOYMENT_SUMMARY.md # 배포 정보
```

---

## 🚀 빠른 시작

### 집에서 개발 환경 설정 (5분)

```bash
# 1. 프로젝트 클론
git clone https://github.com/JustinMath-Park/math-map-project.git
cd math-map-project

# 2. 백엔드 설정
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. 인증
firebase login
gcloud auth login
gcloud config set project my-mvp-backend
```

**📖 자세한 가이드**: [QUICK_START_HOME.md](QUICK_START_HOME.md) 또는 [HOME_SETUP_GUIDE.md](HOME_SETUP_GUIDE.md)

---

## 🛠️ 기술 스택

### Backend
- **언어**: Python 3.12
- **프레임워크**: Flask 3.1.0
- **AI**: Google Vertex AI (Gemini 2.5 Flash)
- **데이터베이스**: Firebase Firestore
- **배포**: Google Cloud Run
- **인증**: Firebase Auth

### Frontend
- **언어**: Vanilla JavaScript
- **수식 렌더링**: KaTeX
- **호스팅**: Firebase Hosting
- **스타일**: CSS3

### DevOps
- **버전 관리**: Git & GitHub
- **클라우드**: Google Cloud Platform
- **CI/CD**: 수동 배포 (GitHub Actions 계획 중)

---

## 📱 배포된 애플리케이션

### 프론트엔드
- **MVP Test**: https://mathiter-mvp-test.web.app
- **Level Test**: https://mathiter-level-test.web.app
- **Curriculum Navigator**: https://mathiter-curriculum.web.app

### 백엔드
- **API Server**: https://my-mvp-backend-1093137562151.us-central1.run.app
- **리전**: us-central1
- **상태**: ✅ 정상 작동

---

## 🔧 개발 가이드

### 로컬 개발

#### 백엔드 실행
```bash
cd backend
source venv/bin/activate
python app.py
# http://localhost:5001
```

#### 프론트엔드 실행
```bash
cd apps/mvp-test
python3 -m http.server 8000
# http://localhost:8000
```

### 배포

#### 백엔드 (Cloud Run)
```bash
cd backend
gcloud run deploy my-mvp-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --timeout 120
```

#### 프론트엔드 (Firebase Hosting)
```bash
# 전체 배포
firebase deploy --only hosting

# 개별 앱 배포
firebase deploy --only hosting:mvp-test
firebase deploy --only hosting:level-test
firebase deploy --only hosting:curriculum-navigator
```

---

## 📚 문서

### 핵심 문서
- **[HOME_SETUP_GUIDE.md](HOME_SETUP_GUIDE.md)**: 개발 환경 설정 전체 가이드
- **[QUICK_START_HOME.md](QUICK_START_HOME.md)**: 5분 빠른 시작 가이드
- **[PROJECT_STATUS.md](PROJECT_STATUS.md)**: 프로젝트 현재 상태
- **[DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)**: Firebase 배포 정보

### 기술 문서
- **[CORS_ISSUE_RESOLVED.md](CORS_ISSUE_RESOLVED.md)**: CORS 문제 해결 과정
- **[math-curriculum-roadmap/README.md](math-curriculum-roadmap/README.md)**: 커리큘럼 프로젝트

---

## 🤝 기여하기

### Git 워크플로우

```bash
# 최신 코드 받기
git pull origin main

# 새 브랜치 생성
git checkout -b feature/your-feature

# 작업 후 커밋
git add .
git commit -m "Add: 기능 설명"
git push origin feature/your-feature

# GitHub에서 Pull Request 생성
```

### 커밋 메시지 규칙
- `Add:` 새로운 기능 추가
- `Fix:` 버그 수정
- `Update:` 기존 기능 개선
- `Refactor:` 코드 리팩토링
- `Docs:` 문서 수정

---

## 🔍 주요 API 엔드포인트

### 문제 관련
- `GET /get_test_problems` - 테스트 문제 조회
- `POST /submit_and_analyze` - 답안 제출 및 AI 분석

### 사용자 관련
- `POST /register_guest` - 게스트 사용자 등록
- `GET /user/profile` - 사용자 프로필 조회
- `POST /user/profile` - 사용자 프로필 저장

### 커리큘럼 관련
- `GET /curriculums` - 모든 커리큘럼 목록
- `GET /curriculums/<id>` - 특정 커리큘럼 상세
- `GET /lectures/<id>` - 강의 상세 정보

---

## 🎯 로드맵

### 완료 ✅
- [x] CORS 문제 해결
- [x] Firebase 멀티사이트 배포
- [x] Vertex AI 마이그레이션
- [x] Curriculum Roadmap 추가
- [x] 개발 환경 설정 가이드

### 진행 중 🔄
- [ ] 사용자 피드백 수집
- [ ] 성능 최적화
- [ ] 에러 핸들링 개선

### 계획 📋
- [ ] Google Analytics 4 연동
- [ ] 커스텀 도메인 연결
- [ ] 단위 테스트 추가
- [ ] CI/CD 파이프라인 (GitHub Actions)
- [ ] 다국어 지원 (i18n)

---

## 📊 프로젝트 현황

- **총 앱 수**: 3개 (모두 배포 완료)
- **백엔드 상태**: ✅ 정상 작동
- **CORS**: ✅ 해결 완료
- **최근 업데이트**: 2025-11-21
- **다음 마일스톤**: 사용자 피드백 수집

---

## 🔗 유용한 링크

### 콘솔
- [Firebase Console](https://console.firebase.google.com/project/my-mvp-backend)
- [Cloud Run Console](https://console.cloud.google.com/run?project=my-mvp-backend)
- [GitHub Repository](https://github.com/JustinMath-Park/math-map-project)

### 문서
- [Firebase Documentation](https://firebase.google.com/docs)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)

---

## 📝 라이선스

이 프로젝트는 개인 학습 및 연구 목적으로 작성되었습니다.

---

## 📞 문제 해결

문제가 발생하면 다음 문서를 참고하세요:

1. **개발 환경**: [HOME_SETUP_GUIDE.md](HOME_SETUP_GUIDE.md) → 문제 해결 섹션
2. **CORS 관련**: [CORS_ISSUE_RESOLVED.md](CORS_ISSUE_RESOLVED.md)
3. **배포 관련**: [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)

---

## 🎉 상태

**모든 시스템 정상 작동 중!** ✅

- ✅ Backend API: 정상
- ✅ CORS Headers: 정상
- ✅ 3개 앱 배포: 정상
- ✅ GitHub 동기화: 완료

---

**Built with ❤️ using Claude Code**

Last Updated: 2025-11-21
