# ⚡ 집에서 바로 시작하기 (Quick Start)

5분 안에 집 컴퓨터에서 개발 환경을 설정하는 방법입니다.

---

## 🚀 1단계: 필수 도구 설치 (5분)

### macOS
```bash
# Homebrew로 모든 것 한 번에 설치
brew install git python@3.12 node
npm install -g firebase-tools
brew install --cask google-cloud-sdk
```

### Windows
1. Git: https://git-scm.com/download/win
2. Python: https://www.python.org/downloads/
3. Node.js: https://nodejs.org/
4. 터미널에서: `npm install -g firebase-tools`
5. Google Cloud SDK: https://cloud.google.com/sdk/docs/install

---

## 📥 2단계: 프로젝트 받기 (1분)

```bash
# 프로젝트 클론
cd ~/projects  # 원하는 디렉토리
git clone https://github.com/JustinMath-Park/math-map-project.git
cd math-map-project
```

---

## 🔧 3단계: 백엔드 설정 (3분)

```bash
# 가상환경 생성 및 활성화
cd backend
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt

# .env 파일 생성
cat > .env << 'EOF'
PROJECT_ID=my-mvp-backend
MODEL_NAME_FLASH=gemini-2.5-flash
AI_LOCATION=us-central1
PORT=5001
DEBUG=True
EOF
```

---

## 🔐 4단계: 인증 (2분)

```bash
# Firebase 로그인
firebase login

# Google Cloud 로그인
gcloud auth login
gcloud auth application-default login
gcloud config set project my-mvp-backend
```

---

## ✅ 완료! 이제 작업 시작

### 로컬에서 백엔드 실행
```bash
cd backend
source venv/bin/activate
python app.py
# http://localhost:5001 접속
```

### 로컬에서 프론트엔드 실행
```bash
cd apps/mvp-test
python3 -m http.server 8000
# http://localhost:8000 접속
```

---

## 📝 매일 작업 루틴

### 작업 시작 시
```bash
cd ~/projects/math-map-project
git pull origin main
cd backend && source venv/bin/activate
```

### 작업 완료 후
```bash
git add .
git commit -m "작업 내용"
git push origin main
```

---

## 🔗 더 자세한 내용은?

전체 가이드: [HOME_SETUP_GUIDE.md](HOME_SETUP_GUIDE.md)

---

## 📱 현재 배포된 앱들

- **MVP Test**: https://mathiter-mvp-test.web.app
- **Level Test**: https://mathiter-level-test.web.app
- **Curriculum Navigator**: https://mathiter-curriculum.web.app
- **Backend API**: https://my-mvp-backend-1093137562151.us-central1.run.app

---

## 💡 자주 사용하는 명령어

```bash
# 최신 코드 받기
git pull

# 백엔드 배포
cd backend
gcloud run deploy my-mvp-backend --source . --region us-central1 --allow-unauthenticated

# 프론트엔드 배포
firebase deploy --only hosting:mvp-test

# 로그 확인
gcloud run services logs read my-mvp-backend --region=us-central1 --limit=50
```

---

**🎉 준비 완료! 이제 코딩을 시작하세요!**
