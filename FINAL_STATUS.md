# 최종 상태 및 남은 작업

## ✅ 완료된 작업

### 1. Firebase Hosting 배포 (3개 앱)
- ✅ MVP Test: https://mathiter-mvp-test.web.app
- ✅ Level Test: https://mathiter-level-test.web.app
- ✅ Curriculum Navigator: https://mathiter-curriculum.web.app

### 2. 백엔드 서비스 식별
- **US-Central1**: https://my-mvp-backend-1093137562151.us-central1.run.app (현재 사용 중)
- **Asia-Northeast3**: https://my-mvp-backend-llxfuzlavq-du.a.run.app (사용 안함)

### 3. MVP 테스트 앱 URL 업데이트
- ✅ 최신 백엔드 URL로 업데이트
- ✅ Firebase Hosting 재배포 완료

## ⚠️ 남은 문제

### CORS 헤더 누락
**문제**: 백엔드에서 `Access-Control-Allow-Origin` 헤더를 보내지 않음

**원인**:
1. backend/app.py의 CORS 설정 변경 완료
2. 하지만 Cloud Run에 배포된 이미지는 **이전 코드**
3. 새로 빌드된 이미지가 배포되지 않음

**해결 방법**:

### 방법 1: 백엔드 코드 재빌드 및 배포 (추천)
```bash
cd backend
gcloud run deploy my-mvp-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --timeout 120
```

### 방법 2: Cloud Run Console에서 수동 설정
1. https://console.cloud.google.com/run 접속
2. `my-mvp-backend` (us-central1) 선택
3. EDIT & DEPLOY NEW REVISION
4. Container 탭에서 Command 추가:
   ```
   gunicorn --bind :$PORT app:app
   ```
5. Deploy

### 방법 3: 프론트엔드 우회 (임시)
CORS 문제를 우회하는 방법:
- Firebase Functions를 프록시로 사용
- 또는 샘플 데이터를 프론트엔드에 내장

## 🔍 현재 에러

브라우저 Console:
```
Access to 'https://my-mvp-backend-1093137562151.us-central1.run.app/get_test_problems'
from origin 'https://mathiter-mvp-test.web.app' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## 📋 다음 단계

1. **백엔드 재배포** (코드 변경 사항 적용)
   - backend/app.py의 CORS 설정이 포함된 새 이미지 빌드
   - Cloud Run에 배포

2. **테스트**
   - https://mathiter-mvp-test.web.app 접속
   - "레벨 테스트 시작하기" 클릭
   - 문제 로딩 확인

3. **CORS 헤더 확인**
   ```bash
   curl -H "Origin: https://mathiter-mvp-test.web.app" -v \
     https://my-mvp-backend-1093137562151.us-central1.run.app/get_test_problems \
     2>&1 | grep "access-control-allow-origin"
   ```

## 💡 백엔드 배포 실패 원인

최근 배포 시도들이 모두 실패한 이유:
- Dockerfile의 PORT 설정 문제
- Gunicorn이 8080 포트에서 시작하지 못함
- Health check timeout

**해결책**: Dockerfile 확인 및 수정 필요
