# 🏠 집에서 빠르게 시작하기

새 컴퓨터에서 프로젝트를 빠르게 설정하는 방법입니다.

## 1️⃣ 빠른 설치 (10분)

```bash
# 1. 프로젝트 클론
git clone https://github.com/JustinMath-Park/math-map-project.git
cd math-map-project

# 2. 백엔드 설정
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. 필요한 파일 복사
# - backend/your-service-account-key.json (Firebase 키)
# - backend/.env (Gemini API 키)
```

## 2️⃣ 필수 파일 2개

### backend/your-service-account-key.json
회사 컴퓨터에서 복사하거나 [Firebase Console](https://console.firebase.google.com/)에서 새로 생성

### backend/.env
```bash
GEMINI_API_KEY=회사_컴퓨터에서_복사
```

## 3️⃣ 로컬 실행

```bash
# 백엔드 실행
cd backend
source venv/bin/activate
python app.py

# 프론트엔드는 배포된 버전 사용
# https://my-mvp-backend.web.app
```

## 4️⃣ 코드 변경 후

```bash
git add .
git commit -m "작업 내용"
git push origin main

# 배포 (필요시)
cd backend
gcloud run deploy my-mvp-backend --source . --region=asia-northeast3 --allow-unauthenticated
```

## 📚 자세한 가이드

전체 설정 가이드: [SETUP_NEW_ENVIRONMENT.md](SETUP_NEW_ENVIRONMENT.md)

## ⚡ 문제 해결

```bash
# Firebase 키 오류
→ backend/your-service-account-key.json 파일 확인

# Gemini API 오류
→ backend/.env 파일 확인

# gcloud 오류
gcloud auth login
gcloud config set project my-mvp-backend
```

## 🔗 주요 링크

- **배포된 프론트엔드**: https://my-mvp-backend.web.app
- **배포된 백엔드 API**: https://my-mvp-backend-1093137562151.asia-northeast3.run.app
- **커리큘럼 브라우저**: https://my-mvp-backend.web.app/curriculum.html
- **GitHub**: https://github.com/JustinMath-Park/math-map-project
- **Firebase Console**: https://console.firebase.google.com/project/my-mvp-backend
- **Google Cloud Console**: https://console.cloud.google.com/run?project=my-mvp-backend

---

**작성일**: 2025-11-13
