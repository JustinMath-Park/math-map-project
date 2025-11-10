# Python 3.12 이미지 사용 (안정 버전)
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사
COPY requirements.txt .

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 환경 변수 설정
ENV PORT=8080

# Gunicorn으로 실행
CMD exec gunicorn --bind :$PORT --workers 2 --timeout 120 --worker-class sync app:app