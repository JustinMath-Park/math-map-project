# 🏠 집에서 개발 환경 설정 가이드

이 가이드는 집 컴퓨터에서 프로젝트를 받아서 개발을 이어갈 수 있도록 도와줍니다.

---

## 📋 목차

1. [초기 설정 (최초 1회만)](#초기-설정-최초-1회만)
2. [일상적인 작업 플로우](#일상적인-작업-플로우)
3. [프로젝트 구조](#프로젝트-구조)
4. [주요 명령어 모음](#주요-명령어-모음)
5. [문제 해결](#문제-해결)

---

## 🚀 초기 설정 (최초 1회만)

### 1. 필수 도구 설치

#### macOS (Homebrew 사용)
```bash
# Homebrew 설치 (없는 경우)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Git 설치
brew install git

# Python 3.12+ 설치
brew install python@3.12

# Node.js 및 npm 설치 (Firebase CLI용)
brew install node

# Firebase CLI 설치
npm install -g firebase-tools

# Google Cloud SDK 설치
brew install --cask google-cloud-sdk
```

#### Windows
1. **Git**: https://git-scm.com/download/win
2. **Python 3.12+**: https://www.python.org/downloads/
3. **Node.js**: https://nodejs.org/
4. **Firebase CLI**: `npm install -g firebase-tools`
5. **Google Cloud SDK**: https://cloud.google.com/sdk/docs/install

### 2. Git 설정

```bash
# Git 사용자 정보 설정
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# GitHub SSH 키 설정 (권장)
ssh-keygen -t ed25519 -C "your.email@example.com"
# Enter 3번 누르기

# SSH 키를 GitHub에 등록
cat ~/.ssh/id_ed25519.pub
# 출력된 내용을 복사해서 https://github.com/settings/keys 에서 "New SSH key" 클릭하여 등록
```

### 3. 프로젝트 클론

```bash
# 작업 디렉토리로 이동
cd ~/projects  # 또는 원하는 디렉토리

# GitHub에서 프로젝트 클론
git clone https://github.com/JustinMath-Park/math-map-project.git

# 프로젝트 디렉토리로 이동
cd math-map-project
```

### 4. Python 가상환경 설정

```bash
# 백엔드 디렉토리로 이동
cd backend

# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 5. 환경 변수 설정

```bash
# backend/.env 파일 생성
cd backend
cat > .env << 'EOF'
PROJECT_ID=my-mvp-backend
MODEL_NAME_FLASH=gemini-2.5-flash
AI_LOCATION=us-central1
FRONTEND_URL=https://my-mvp-backend.web.app
WIX_SITE_URL=https://www.mathiter.com
PORT=5001
DEBUG=True
EOF
```

### 6. Firebase 및 Google Cloud 인증

```bash
# Firebase 로그인
firebase login

# Firebase 프로젝트 확인
firebase projects:list

# Google Cloud 인증
gcloud auth login
gcloud auth application-default login

# 프로젝트 설정
gcloud config set project my-mvp-backend
```

### 7. Service Account Key 다운로드

1. Google Cloud Console 접속: https://console.cloud.google.com
2. "IAM 및 관리자" → "서비스 계정" 선택
3. 프로젝트의 서비스 계정 찾기
4. "키 관리" → "키 추가" → "JSON" 선택
5. 다운로드된 JSON 파일을 `backend/your-service-account-key.json`으로 저장

```bash
# 환경 변수 설정 (매번 터미널 실행 시 필요)
export GOOGLE_APPLICATION_CREDENTIALS="/absolute/path/to/backend/your-service-account-key.json"
```

---

## 🔄 일상적인 작업 플로우

### 아침에 작업 시작 시

```bash
# 1. 프로젝트 디렉토리로 이동
cd ~/projects/math-map-project

# 2. 최신 변경사항 가져오기
git pull origin main

# 3. 가상환경 활성화 (백엔드 작업 시)
cd backend
source venv/bin/activate

# 4. 새로운 의존성이 추가되었을 수 있으므로
pip install -r requirements.txt
```

### 작업 중

```bash
# 백엔드 로컬 서버 실행 (테스트용)
cd backend
python app.py
# http://localhost:5001 에서 접근 가능

# 프론트엔드 로컬 서버 실행
cd apps/mvp-test
python3 -m http.server 8000
# http://localhost:8000 에서 접근 가능
```

### 작업 완료 후

```bash
# 1. 변경사항 확인
git status
git diff

# 2. 변경사항 스테이징
git add .

# 3. 커밋
git commit -m "작업 내용 설명"

# 4. GitHub에 푸시
git push origin main
```

---

## 📁 프로젝트 구조

```
math-map-project/
├── backend/                    # Flask 백엔드 (Cloud Run)
│   ├── app.py                 # 메인 애플리케이션
│   ├── config.py              # 설정 파일
│   ├── requirements.txt       # Python 의존성
│   ├── Dockerfile            # Cloud Run 배포용
│   ├── routes/               # API 엔드포인트
│   ├── services/             # 비즈니스 로직
│   ├── utils/                # 유틸리티 함수
│   └── .env                  # 환경 변수 (git ignore)
│
├── apps/                      # Firebase Hosting 앱들
│   ├── mvp-test/             # MVP 테스트 앱
│   ├── level-test/           # 레벨 테스트 앱
│   └── curriculum-navigator/ # 커리큘럼 네비게이터
│
├── math-curriculum-roadmap/   # 커리큘럼 로드맵 프로젝트
│   ├── frontend/             # 정적 파일
│   ├── scripts/              # 데이터 시딩 스크립트
│   └── docs/                 # 프로젝트 문서
│
├── firebase.json              # Firebase 멀티사이트 설정
├── .firebaserc               # Firebase 프로젝트 타겟
│
└── 📝 문서들/
    ├── CORS_ISSUE_RESOLVED.md      # CORS 문제 해결 기록
    ├── DEPLOYMENT_SUMMARY.md       # Firebase 배포 정보
    └── HOME_SETUP_GUIDE.md         # 이 파일!
```

---

## 🛠 주요 명령어 모음

### Git 작업

```bash
# 최신 코드 가져오기
git pull origin main

# 변경사항 확인
git status
git diff

# 커밋 및 푸시
git add .
git commit -m "메시지"
git push origin main

# 브랜치 생성 및 전환
git checkout -b feature/new-feature
git push -u origin feature/new-feature

# 변경사항 되돌리기 (주의!)
git checkout -- <file>  # 특정 파일만
git reset --hard HEAD   # 모든 변경사항 삭제
```

### 백엔드 작업

```bash
# 로컬 서버 실행
cd backend
source venv/bin/activate
python app.py

# Cloud Run에 배포
cd backend
gcloud run deploy my-mvp-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --timeout 120

# 로그 확인
gcloud run services logs read my-mvp-backend --region=us-central1 --limit=50
```

### Firebase Hosting 작업

```bash
# 로컬 미리보기
firebase serve --only hosting

# 전체 배포
firebase deploy --only hosting

# 특정 앱만 배포
firebase deploy --only hosting:mvp-test
firebase deploy --only hosting:level-test
firebase deploy --only hosting:curriculum-navigator

# 배포 히스토리 확인
firebase hosting:channel:list
```

### Python 의존성 관리

```bash
# 새 패키지 설치
pip install package-name

# requirements.txt 업데이트
pip freeze > requirements.txt

# requirements.txt에서 설치
pip install -r requirements.txt

# 가상환경 재생성 (문제 발생 시)
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## ❗ 문제 해결

### Git Pull 실패

```bash
# 로컬 변경사항과 충돌하는 경우
git stash          # 현재 작업 임시 저장
git pull           # 최신 코드 가져오기
git stash pop      # 임시 저장한 작업 복원
```

### 가상환경 활성화 안됨

```bash
# macOS/Linux
source backend/venv/bin/activate

# Windows
backend\venv\Scripts\activate

# 프롬프트 앞에 (venv) 표시되면 성공
```

### Firebase 배포 실패

```bash
# 재인증
firebase login --reauth

# 프로젝트 확인
firebase use my-mvp-backend

# 타겟 재설정
firebase target:apply hosting mvp-test mathiter-mvp-test
firebase target:apply hosting level-test mathiter-level-test
firebase target:apply hosting curriculum-navigator mathiter-curriculum
```

### Cloud Run 배포 실패

```bash
# 인증 재설정
gcloud auth login
gcloud auth application-default login

# 프로젝트 확인
gcloud config set project my-mvp-backend

# 빌드 로그 확인
gcloud builds list --limit=1
gcloud builds log <BUILD_ID>
```

### 백엔드 503 에러

```bash
# Cloud Run 로그 확인
gcloud run services logs read my-mvp-backend --region=us-central1 --limit=100

# 일반적인 원인:
# 1. requirements.txt에 패키지 누락
# 2. 환경 변수 미설정
# 3. Service Account 권한 문제
```

---

## 🎯 개발 팁

### 1. 브랜치 전략

```bash
# 새 기능 개발 시
git checkout -b feature/feature-name
# 작업...
git push -u origin feature/feature-name
# GitHub에서 Pull Request 생성

# 긴급 버그 수정 시
git checkout -b hotfix/bug-description
# 수정...
git push -u origin hotfix/bug-description
```

### 2. 로컬 테스트 먼저

배포 전에 항상 로컬에서 테스트:
```bash
# 백엔드 테스트
cd backend
python app.py
# 브라우저: http://localhost:5001/health

# 프론트엔드 테스트
cd apps/mvp-test
python3 -m http.server 8000
# 브라우저: http://localhost:8000
```

### 3. 정기적인 Pull

충돌을 최소화하기 위해:
```bash
# 아침마다
git pull origin main

# 작업 시작 전
git pull origin main

# 푸시 전
git pull origin main
```

### 4. 의미 있는 커밋 메시지

```bash
# ❌ 나쁜 예
git commit -m "fix"
git commit -m "update"

# ✅ 좋은 예
git commit -m "Fix CORS issue by adding Flask-CORS to requirements"
git commit -m "Add new API endpoint for user profile"
git commit -m "Update frontend to use new backend URL"
```

---

## 📞 도움이 필요할 때

### 문서 확인
- [CORS_ISSUE_RESOLVED.md](CORS_ISSUE_RESOLVED.md): CORS 문제 해결 방법
- [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md): Firebase 배포 가이드
- [math-curriculum-roadmap/README.md](math-curriculum-roadmap/README.md): 커리큘럼 프로젝트 설명

### 유용한 링크
- **Firebase Console**: https://console.firebase.google.com/project/my-mvp-backend
- **Cloud Run Console**: https://console.cloud.google.com/run?project=my-mvp-backend
- **GitHub Repository**: https://github.com/JustinMath-Park/math-map-project

### 현재 배포된 앱들
- **MVP Test**: https://mathiter-mvp-test.web.app
- **Level Test**: https://mathiter-level-test.web.app
- **Curriculum Navigator**: https://mathiter-curriculum.web.app
- **Backend API**: https://my-mvp-backend-1093137562151.us-central1.run.app

---

## ✅ 체크리스트

### 초기 설정 완료 체크
- [ ] Git 설치 및 설정
- [ ] Python 3.12+ 설치
- [ ] Node.js 및 Firebase CLI 설치
- [ ] Google Cloud SDK 설치
- [ ] 프로젝트 클론
- [ ] Python 가상환경 생성
- [ ] 의존성 설치
- [ ] .env 파일 생성
- [ ] Firebase 로그인
- [ ] Google Cloud 인증
- [ ] Service Account Key 다운로드

### 매일 작업 전 체크
- [ ] `git pull origin main` 실행
- [ ] 가상환경 활성화
- [ ] `pip install -r requirements.txt` (필요시)

### 작업 완료 후 체크
- [ ] 로컬 테스트 완료
- [ ] `git status`로 변경사항 확인
- [ ] `git add .`로 스테이징
- [ ] 의미 있는 커밋 메시지 작성
- [ ] `git push origin main`

---

## 🎉 준비 완료!

이제 집에서도 프로젝트 개발을 이어갈 수 있습니다!

질문이나 문제가 발생하면 이 가이드를 참고하세요.
Happy coding! 🚀
