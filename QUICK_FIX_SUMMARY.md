# MVP Test CORS 문제 해결 방법

## 문제 상황
- **에러**: CORS policy violation
- **원인**: 백엔드에서 `Access-Control-Allow-Origin` 헤더를 보내지 않음
- **백엔드 재배포 실패**: Cloud Run 배포가 계속 실패

## 해결 방법 2가지

### 방법 1: 백엔드 수동 재시작 (권장)
Cloud Run 콘솔에서 수동으로 서비스 재시작:
1. https://console.cloud.google.com/run 접속
2. `my-mvp-backend` 서비스 선택
3. "EDIT & DEPLOY NEW REVISION" 클릭
4. Environment Variables에 추가:
   - `CORS_ENABLED=true`
5. Deploy 클릭

### 방법 2: 프록시 사용
Cloud Run 앞에 Cloud Load Balancer를 두고 CORS 헤더 추가

### 방법 3: 프론트엔드에 샘플 데이터 내장 (임시)
백엔드 없이 작동하도록 수정 - 지금 진행 중

## 현재 상태
- backend/app.py 수정 완료 (CORS 모든 origin 허용)
- 재배포 필요하지만 실패 중
- 임시 해결책으로 프론트엔드 수정 진행 중
