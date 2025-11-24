# 🔄 작업 방식 권장사항: 로컬 vs 온라인 호스팅

## 📊 현재 상황

### Firebase Hosting 사이트 (4개)
1. ✅ **mathiter-mvp-test** - MVP 테스트 앱
2. ✅ **mathiter-level-test** - 레벨 테스트 앱
3. ✅ **mathiter-curriculum** - 커리큘럼 네비게이터
4. 🆕 **adaptive-test** - 적응형 테스트 (firebase.json에 설정됨, 아직 미배포)

### 추가 사이트
- **my-mvp-backend** - 기본 Firebase 사이트 (현재 사용 안함)

---

## 🤔 질문: 로컬 작업 vs 온라인 호스팅?

### 답변: **로컬 개발 → 테스트 → 배포** 방식이 **훨씬 효율적**입니다! ✅

---

## 💡 권장하는 작업 플로우

### ⭐ 최적의 워크플로우

```
1. 로컬에서 개발 및 테스트
   ↓
2. GitHub에 커밋
   ↓
3. Firebase Hosting에 배포
   ↓
4. 실제 사용자 테스트
```

---

## 📋 각 단계별 상세 가이드

### 1️⃣ 로컬에서 개발 (가장 빠름! ⚡)

#### Frontend 개발
```bash
# 앱 디렉토리로 이동
cd apps/level-test   # 또는 mvp-test, curriculum-navigator, adaptive-test

# 로컬 서버 실행
python3 -m http.server 8000

# 브라우저에서 확인
# http://localhost:8000
```

#### Backend 개발
```bash
# 백엔드 디렉토리로 이동
cd backend

# 가상환경 활성화
source venv/bin/activate

# 로컬 서버 실행
python app.py

# 또는 run_local.py 사용 (주말에 추가됨)
python ../run_local.py

# 브라우저에서 확인
# http://localhost:5001
```

### 2️⃣ 로컬에서 통합 테스트

```bash
# Terminal 1: Backend 실행
cd backend && source venv/bin/activate && python app.py

# Terminal 2: Frontend 실행
cd apps/level-test && python3 -m http.server 8000

# 브라우저에서 http://localhost:8000 접속
# Backend는 http://localhost:5001 호출
```

### 3️⃣ Git에 커밋

```bash
# 변경사항 확인
git status
git diff

# 스테이징
git add apps/level-test/
git add backend/

# 커밋
git commit -m "feat: Add new feature to level-test"

# GitHub에 푸시
git push origin main
```

### 4️⃣ Firebase에 배포

```bash
# 특정 앱만 배포
firebase deploy --only hosting:level-test

# 여러 앱 동시 배포
firebase deploy --only hosting:level-test,hosting:adaptive-test

# 전체 배포
firebase deploy --only hosting

# 백엔드 배포 (Cloud Run)
cd backend
gcloud run deploy my-mvp-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --timeout 120
```

---

## ✅ 로컬 개발의 장점

### 1. **속도 ⚡**
- 즉시 새로고침으로 변경사항 확인
- 배포 대기 시간 없음 (Firebase 배포는 1-2분 소요)

### 2. **비용 절감 💰**
- Firebase Hosting은 무료 할당량이 있지만, 잦은 배포는 비효율적
- Cloud Run도 호출당 과금

### 3. **디버깅 용이 🔍**
- 브라우저 개발자 도구로 즉시 디버깅
- Backend 로그 실시간 확인 (`python app.py`)
- 네트워크 요청/응답 바로 확인

### 4. **실험 자유로움 🧪**
- 마음껏 코드 수정하고 테스트
- 실패해도 로컬에서만 영향
- 사용자에게 영향 없음

### 5. **오프라인 작업 가능 ✈️**
- 인터넷 없이도 개발 가능
- Frontend는 로컬 서버로 충분
- Backend도 로컬 Firestore Emulator 사용 가능

---

## ❌ 온라인에서 바로 수정하는 방식의 단점

### 1. **느림 🐌**
- 매번 배포 대기 (1-2분)
- 캐시 때문에 변경사항 즉시 반영 안됨

### 2. **위험 ⚠️**
- 실수로 프로덕션 환경 망가뜨릴 수 있음
- 사용자가 바로 영향 받음

### 3. **디버깅 어려움 😰**
- 로그 확인이 번거로움 (Cloud Run 콘솔 접속 필요)
- 빠른 반복 테스트 불가능

### 4. **비효율적인 Git 히스토리 📝**
- "fix typo", "fix again", "really fix" 같은 커밋 남발

---

## 🎯 상황별 권장 작업 방식

### 시나리오 1: 새 기능 개발
```
✅ 권장: 로컬에서 개발 → 테스트 → Git 커밋 → 배포
❌ 비권장: 바로 온라인 호스팅에서 수정
```

### 시나리오 2: 버그 수정
```
✅ 권장: 로컬에서 재현 → 수정 → 테스트 → Git 커밋 → 배포
❌ 비권장: 호스팅에서 직접 수정
```

### 시나리오 3: UI 스타일 조정
```
✅ 권장: 로컬 서버 + 브라우저 개발자 도구로 실시간 조정
❌ 비권장: 배포 → 확인 → 수정 → 재배포 반복
```

### 시나리오 4: 긴급 핫픽스
```
⚠️ 예외: 아주 작은 수정(오타 등)은 빠른 배포 가능
✅ 원칙: 로컬 테스트 후 배포가 더 안전
```

---

## 🚀 효율적인 개발 환경 설정

### VS Code로 작업하기 (추천)

#### 1. 프로젝트 폴더 열기
```bash
cd ~/projects/math-map-project
code .
```

#### 2. 터미널 분할
- Terminal 1: Backend 실행
- Terminal 2: Frontend 실행
- Terminal 3: Git 명령어

#### 3. 확장 프로그램 추천
- **Live Server**: HTML 파일 자동 새로고침
- **Python**: Python 개발 지원
- **GitLens**: Git 히스토리 시각화
- **Prettier**: 코드 포맷팅

### 브라우저 개발자 도구 활용

```
F12 또는 Cmd+Option+I (Mac)

- Console: JavaScript 에러 확인
- Network: API 요청/응답 확인
- Elements: HTML/CSS 실시간 수정
- Application: LocalStorage, Cookies 확인
```

---

## 📖 실전 예시

### 예시 1: level-test 앱에 새 기능 추가

```bash
# 1. 로컬에서 개발
cd apps/level-test
code index.html  # VS Code로 열기
python3 -m http.server 8000

# 2. 브라우저에서 http://localhost:8000 확인
# 3. 수정 → 새로고침 반복

# 4. 완성되면 Git 커밋
git add apps/level-test/
git commit -m "feat: Add progress bar to level-test"
git push origin main

# 5. Firebase 배포
firebase deploy --only hosting:level-test

# 6. 실제 사이트 확인
# https://mathiter-level-test.web.app
```

### 예시 2: Backend API 추가

```bash
# 1. 로컬에서 개발
cd backend
source venv/bin/activate
code routes/api_routes.py

# 2. 로컬 서버 실행
python app.py

# 3. Postman 또는 curl로 테스트
curl http://localhost:5001/new-endpoint

# 4. 테스트 작성
pytest tests/test_new_endpoint.py

# 5. Git 커밋
git add backend/
git commit -m "feat: Add new endpoint for user analytics"
git push origin main

# 6. Cloud Run 배포
./deploy_backend.sh
# 또는
gcloud run deploy my-mvp-backend --source . --region us-central1
```

---

## 🔄 주말 작업으로 추가된 도구들

### 1. `run_local.py` - 로컬 개발 서버
```bash
python run_local.py
# Backend와 Frontend를 한 번에 실행
```

### 2. `deploy.sh` - 전체 배포 스크립트
```bash
./deploy.sh
# Backend + Frontend 모두 배포
```

### 3. `deploy_backend.sh` - Backend만 배포
```bash
./deploy_backend.sh
# Cloud Run에 Backend만 배포
```

### 4. `verify_api.py` - API 검증
```bash
python verify_api.py
# 배포 후 API 동작 확인
```

### 5. pytest 테스트 환경
```bash
cd backend
pytest -v
# 자동화된 테스트 실행
```

---

## 💾 로컬 개발 시 주의사항

### 1. 환경 변수 설정

```bash
# backend/.env 파일 확인
cd backend
cat .env

# 필수 환경 변수:
# - PROJECT_ID
# - MODEL_NAME_FLASH
# - AI_LOCATION
```

### 2. Backend URL 설정

로컬 개발 시 Frontend의 API URL을 `localhost`로 변경:

```javascript
// apps/level-test/js/config.js
const config = {
  development: {
    API_BASE: 'http://localhost:5001',  // 로컬 개발
  },
  production: {
    API_BASE: 'https://my-mvp-backend-1093137562151.us-central1.run.app',  // 배포
  }
};

// 현재 환경 자동 감지
const isLocalhost = window.location.hostname === 'localhost';
const currentConfig = isLocalhost ? config.development : config.production;
```

### 3. CORS 설정 (이미 해결됨)

Backend의 CORS가 `localhost`도 허용하도록 설정되어 있음:
```python
# backend/app.py
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)
```

---

## 📊 비교표

| 항목 | 로컬 개발 | 온라인 호스팅 직접 수정 |
|------|----------|----------------------|
| **속도** | ⚡⚡⚡ 즉시 | 🐌 1-2분 대기 |
| **디버깅** | ✅ 쉬움 | ❌ 어려움 |
| **비용** | 💰 무료 | 💰 배포 비용 |
| **위험성** | ✅ 안전 | ⚠️ 프로덕션 영향 |
| **오프라인** | ✅ 가능 | ❌ 불가능 |
| **실험** | ✅ 자유로움 | ❌ 제한적 |
| **Git 히스토리** | ✅ 깔끔 | ❌ 지저분 |

---

## 🎯 결론 및 권장사항

### ✅ **로컬 개발을 메인으로 사용하세요!**

1. **일상적인 개발**: 100% 로컬
2. **테스트**: 로컬에서 충분히 테스트
3. **배포**: Git 커밋 후 Firebase/Cloud Run에 배포
4. **사용자 피드백**: 배포된 사이트에서 수집

### 🔄 권장 작업 사이클

```
아침:
1. git pull origin main
2. cd backend && source venv/bin/activate
3. python app.py (백엔드 실행)
4. cd apps/level-test && python3 -m http.server 8000 (프론트엔드 실행)

개발 중:
- 코드 수정 → 브라우저 새로고침 반복
- 디버깅 → 수정 → 테스트 반복

저녁:
1. git add .
2. git commit -m "오늘 작업 내용"
3. git push origin main
4. firebase deploy --only hosting:level-test (필요시)
```

### 📝 체크리스트

개발 시작 전:
- [ ] `git pull` 실행
- [ ] 가상환경 활성화
- [ ] `.env` 파일 확인
- [ ] 로컬 서버 실행

개발 완료 후:
- [ ] 로컬 테스트 완료
- [ ] Git 커밋
- [ ] GitHub 푸시
- [ ] 배포 (필요시)
- [ ] 배포 사이트 확인

---

## 🚀 다음 단계

1. **adaptive-test 앱 배포**
   ```bash
   firebase deploy --only hosting:adaptive-test
   ```

2. **로컬 개발 환경 최적화**
   - VS Code 확장 프로그램 설치
   - 터미널 설정 개선
   - Git aliases 설정

3. **자동화 고려**
   - GitHub Actions로 자동 배포 (선택사항)
   - pre-commit hooks로 코드 품질 검사

---

**요약**: 로컬에서 개발 → 테스트 → Git → 배포 순서가 **가장 효율적**이고 **안전**합니다! 🎯
