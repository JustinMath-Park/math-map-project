# 다른 환경에서 프로젝트 설정하기

이 가이드는 집 또는 다른 컴퓨터에서 동일한 개발 환경을 설정하는 방법을 안내합니다.

## 목차
1. [사전 준비물](#사전-준비물)
2. [프로젝트 클론](#프로젝트-클론)
3. [백엔드 설정](#백엔드-설정)
4. [프론트엔드 설정](#프론트엔드-설정)
5. [Firebase 설정](#firebase-설정)
6. [환경 변수 설정](#환경-변수-설정)
7. [로컬 실행](#로컬-실행)
8. [배포](#배포)

---

## 사전 준비물

### 필수 소프트웨어 설치

#### 1. Python 3.14
```bash
# macOS (Homebrew)
brew install python@3.14

# Windows - python.org에서 다운로드
# https://www.python.org/downloads/
```

#### 2. Node.js (프론트엔드용)
```bash
# macOS
brew install node

# Windows - nodejs.org에서 다운로드
# https://nodejs.org/
```

#### 3. Git
```bash
# macOS
brew install git

# Windows - git-scm.com에서 다운로드
# https://git-scm.com/
```

#### 4. Google Cloud CLI
```bash
# macOS
brew install --cask google-cloud-sdk

# Windows
# https://cloud.google.com/sdk/docs/install

# 설치 후 초기화
gcloud init
```

#### 5. Firebase CLI
```bash
npm install -g firebase-tools
firebase login
```

---

## 프로젝트 클론

```bash
# 1. 원하는 디렉토리로 이동
cd ~

# 2. 프로젝트 클론
git clone https://github.com/JustinMath-Park/math-map-project.git

# 3. 프로젝트 디렉토리로 이동
cd math-map-project
```

---

## 백엔드 설정

### 1. 가상 환경 생성 및 활성화

```bash
cd backend

# 가상 환경 생성
python3 -m venv venv

# 가상 환경 활성화
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 2. 의존성 패키지 설치

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

만약 `requirements.txt`가 없다면 다음 패키지들을 설치:

```bash
pip install flask flask-cors google-generativeai firebase-admin python-dotenv
```

### 3. Firebase 서비스 계정 키 설정

**중요**: 서비스 계정 키 파일이 필요합니다.

#### 방법 1: 기존 키 파일 복사
회사 컴퓨터에서 이 파일을 복사:
```bash
# 기존 위치: backend/your-service-account-key.json
# 이 파일을 안전하게 새 컴퓨터로 이동
```

#### 방법 2: 새로운 키 생성
1. [Firebase Console](https://console.firebase.google.com/) 접속
2. 프로젝트 선택: `my-mvp-backend`
3. 프로젝트 설정 > 서비스 계정
4. "새 비공개 키 생성" 클릭
5. 다운로드한 JSON 파일을 `backend/` 폴더에 저장
6. 파일 이름을 `your-service-account-key.json`로 변경

### 4. Gemini API 키 설정

```bash
# .env 파일 생성
cat > .env << 'EOF'
GEMINI_API_KEY=your_gemini_api_key_here
EOF
```

**Gemini API 키 확인 방법**:
1. [Google AI Studio](https://makersuite.google.com/app/apikey) 접속
2. API 키 복사
3. `.env` 파일에 붙여넣기

---

## 프론트엔드 설정

```bash
cd ../frontend

# Firebase CLI 로그인 (아직 안 했다면)
firebase login

# Firebase 프로젝트 연결 확인
firebase projects:list

# my-mvp-backend 프로젝트 선택
firebase use my-mvp-backend
```

---

## Firebase 설정

### 1. Firebase 프로젝트 정보 확인

```bash
cd frontend
firebase apps:sdkconfig web
```

이 명령어로 `firebaseConfig` 값을 확인하고 `frontend/index.html`과 `frontend/test.html`의 Firebase 설정이 올바른지 확인하세요.

### 2. Firestore 규칙 배포 (선택사항)

```bash
cd backend
firebase deploy --only firestore:rules
```

---

## 환경 변수 설정

### backend/config.py 확인

```python
# backend/config.py
import os

class Config:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    PROJECT_ID = 'my-mvp-backend'
    SERVICE_ACCOUNT_KEY = 'your-service-account-key.json'
```

모든 경로가 올바른지 확인하세요.

---

## 로컬 실행

### 1. 백엔드 실행

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate

# Flask 앱 실행
python app.py
```

백엔드가 `http://127.0.0.1:5000`에서 실행됩니다.

### 2. 프론트엔드 실행

로컬 테스트는 Firebase Hosting 에뮬레이터 사용:

```bash
cd frontend
firebase emulators:start --only hosting
```

또는 단순 HTTP 서버:

```bash
cd frontend
python3 -m http.server 8080
```

프론트엔드가 `http://localhost:8080`에서 실행됩니다.

**주의**: 프론트엔드에서 백엔드 API를 호출할 때는 배포된 URL을 사용:
```javascript
const API_BASE_URL = 'https://my-mvp-backend-1093137562151.asia-northeast3.run.app';
```

---

## 배포

### 백엔드 배포 (Cloud Run)

```bash
cd backend

# Google Cloud 프로젝트 설정
gcloud config set project my-mvp-backend

# Cloud Run에 배포
gcloud run deploy my-mvp-backend \
  --source . \
  --region=asia-northeast3 \
  --allow-unauthenticated
```

### 프론트엔드 배포 (Firebase Hosting)

```bash
cd frontend

# Firebase 프로젝트 선택
firebase use my-mvp-backend

# Hosting에 배포
firebase deploy --only hosting
```

---

## Git 작업 흐름

### 변경사항 가져오기

```bash
# 최신 코드 가져오기
git pull origin main
```

### 변경사항 커밋 및 푸시

```bash
# 변경 파일 확인
git status

# 변경 파일 추가
git add .

# 커밋
git commit -m "작업 내용 설명"

# 푸시
git push origin main
```

---

## 문제 해결

### 1. Python 버전 문제
```bash
# Python 버전 확인
python3 --version

# 3.14가 아니라면 pyenv 사용
brew install pyenv
pyenv install 3.14.0
pyenv global 3.14.0
```

### 2. Firebase 인증 오류
```bash
# 재로그인
firebase logout
firebase login
```

### 3. gcloud 인증 오류
```bash
# 재인증
gcloud auth login
gcloud auth application-default login
```

### 4. 패키지 설치 오류
```bash
# pip 업그레이드
pip install --upgrade pip

# 캐시 제거 후 재설치
pip cache purge
pip install -r requirements.txt --no-cache-dir
```

---

## 중요 파일 백업

다음 파일들은 Git에 포함되지 않으므로 별도 백업 필요:

1. `backend/your-service-account-key.json` - Firebase 서비스 계정 키
2. `backend/.env` - 환경 변수 (Gemini API 키)
3. `config/workflow_config.json` - 워크플로우 설정 (Jira/Confluence 토큰)

이 파일들을 **안전한 암호화된 저장소**에 보관하세요 (예: 1Password, LastPass).

---

## 체크리스트

새로운 환경 설정 시 다음을 확인하세요:

- [ ] Python 3.14 설치
- [ ] Node.js 설치
- [ ] Git 클론 완료
- [ ] 백엔드 가상 환경 생성
- [ ] 백엔드 패키지 설치
- [ ] Firebase 서비스 계정 키 설정
- [ ] Gemini API 키 설정 (.env)
- [ ] Firebase CLI 로그인
- [ ] gcloud CLI 로그인
- [ ] 로컬에서 백엔드 실행 테스트
- [ ] 배포된 API 접근 테스트
- [ ] 프론트엔드 로컬 실행 테스트

---

## 유용한 명령어 모음

```bash
# 백엔드 로그 확인 (Cloud Run)
gcloud run logs read my-mvp-backend --region=asia-northeast3 --limit=50

# Firebase 로그 확인
firebase functions:log

# Firestore 데이터 백업
gcloud firestore export gs://my-mvp-backend-backup/$(date +%Y%m%d)

# Python 가상 환경 재생성
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 연락처

문제 발생 시:
- GitHub Issues: https://github.com/JustinMath-Park/math-map-project/issues
- Email: sspark222@gmail.com

---

**작성일**: 2025-11-13
**최종 수정**: 2025-11-13
