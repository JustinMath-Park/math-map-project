# Math Curriculum Roadmap - Deployment Guide

## Firebase Hosting 배포 가이드

### 사전 준비

1. **Firebase CLI 설치 확인**
```bash
firebase --version
```

설치되지 않았다면:
```bash
npm install -g firebase-tools
```

2. **Firebase 로그인**
```bash
firebase login
```

### 배포 단계

#### 1. 프로젝트 확인
```bash
cd math-curriculum-roadmap
firebase projects:list
```

현재 프로젝트는 `my-mvp-backend`로 설정되어 있습니다.

#### 2. 로컬 테스트 (선택사항)
```bash
# 로컬에서 호스팅 미리보기
firebase serve --only hosting

# 브라우저에서 http://localhost:5000 으로 접속
```

#### 3. 배포 실행
```bash
# 첫 배포
firebase deploy --only hosting

# 또는 특정 사이트로 배포
firebase deploy --only hosting:math-curriculum
```

#### 4. 배포 확인
배포가 완료되면 다음 URL에서 확인할 수 있습니다:
- https://my-mvp-backend.web.app
- https://my-mvp-backend.firebaseapp.com

### 환경 설정

#### 개발 환경
- API: `http://localhost:5001`
- 데이터: 로컬 JSON 파일 또는 API

#### 프로덕션 환경
- API: Firebase Hosting (정적 파일)
- 데이터: `./data/*.json` (번들링됨)

설정은 [frontend/js/config.js](frontend/js/config.js)에서 자동으로 감지됩니다.

### 데이터 관리

#### Firestore에 데이터 업로드

1. **환경 변수 설정**

부모 디렉토리의 `backend/.env` 파일에:
```bash
PROJECT_ID=my-mvp-backend
SERVICE_ACCOUNT_KEY=your-service-account-key.json
CURRICULUM_COLLECTION=curriculum
LECTURE_COLLECTION=lecture_flows
```

2. **커리큘럼 데이터 업로드**
```bash
cd math-curriculum-roadmap
source venv/bin/activate
python scripts/seed_curriculums.py
```

3. **강의 데이터 업로드**
```bash
python scripts/seed_lectures.py
```

### 문제 해결

#### 배포 실패 시
```bash
# 캐시 정리
firebase hosting:disable
firebase deploy --only hosting

# 또는 강제 재배포
firebase deploy --only hosting --force
```

#### 데이터가 보이지 않을 때
1. 브라우저 개발자 도구 콘솔 확인
2. `data/` 폴더가 `frontend/` 안에 있는지 확인
3. JSON 파일 경로 확인

#### CORS 에러 발생 시
Firebase Hosting에서는 기본적으로 CORS가 허용됩니다.
로컬 파일 시스템에서 직접 열 경우 발생할 수 있으므로 반드시 로컬 서버를 사용하세요:
```bash
# 간단한 로컬 서버
cd frontend
python3 -m http.server 8000
# 또는
npx serve .
```

### 업데이트 배포

코드 수정 후:
```bash
# 변경사항 확인
git status

# 배포
firebase deploy --only hosting

# 배포 히스토리 확인
firebase hosting:channel:list
```

### 추가 기능 (선택사항)

#### 멀티 사이트 호스팅
```bash
# 새 사이트 추가
firebase hosting:sites:create math-curriculum

# .firebaserc 업데이트
firebase target:apply hosting math-curriculum math-curriculum
```

#### 프리뷰 채널 사용
```bash
# 프리뷰 채널 생성
firebase hosting:channel:deploy preview-feature-x

# 7일 후 자동 삭제됨
```

### 모니터링

- Firebase Console: https://console.firebase.google.com
- 프로젝트: my-mvp-backend
- Hosting 섹션에서 배포 상태, 트래픽, 에러 확인

### 비용

Firebase Hosting 무료 티어:
- 저장용량: 10GB
- 전송량: 360MB/day
- 커스텀 도메인 지원

현재 프로젝트 크기는 약 40KB (데이터 포함) 정도로 무료 티어 범위 내입니다.

---

## 다음 단계

1. ✅ 즉시 문제 수정 완료
2. ✅ Firebase 설정 완료
3. 🔄 로컬 테스트 권장
4. 🚀 배포 실행 대기

배포 준비가 완료되었습니다!
