import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """애플리케이션 설정"""
    
    # Firebase 설정
    PROJECT_ID = os.getenv('PROJECT_ID', 'my-mvp-backend')
    SERVICE_ACCOUNT_KEY = os.getenv('SERVICE_ACCOUNT_KEY', 'your-service-account-key.json')
    
    # AI 모델 설정
    # MODEL_PRO = os.getenv('MODEL_NAME_PRO', 'gemini-2.5-pro')
    MODEL_FLASH = os.getenv('MODEL_NAME_FLASH', 'gemini-2.5-flash')
    AI_LOCATION = os.getenv('AI_LOCATION', 'us-central1')
    
    # CORS 설정
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'https://my-mvp-backend.web.app')
    WIX_SITE_URL = os.getenv('WIX_SITE_URL', 'https://www.mathiter.com')
    
    # 서버 설정
    PORT = int(os.getenv('PORT', 5001))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # AI 프롬프트
    SOLUTION_SYSTEM_PROMPT = (
        "당신은 세계 최고의 SAT 수학 튜터입니다. 학생이 방금 틀린 문제를 설명해줘야 합니다.\n\n"
        "**LaTeX 사용 필수 규칙:**\n"
        "- LaTeX 수식에는 숫자와 영문 변수만 사용 ($x$, $25 + 10t$)\n"
        "- 한글, 특수문자는 LaTeX 밖에 작성\n"
        "- 예시: '시간당 대여료는 $10t$입니다' (O)\n"
        "- 예시: '$시간당대여료$는 $10t$' (X)\n\n"
        "**금지 사항:**\n"
        "- HTML 태그 사용 금지 (<br>, <strong> 등)\n"
        "- 과도한 서론/결론 금지\n\n"
        "**답변 스타일:**\n"
        "- 격려하고 친절하며 명확한 톤\n"
        "- 3-5문장으로 핵심만 간결하게\n"
        "- 마크다운 볼드(**) 사용 가능"
    )
    
    ANALYSIS_SYSTEM_PROMPT = (
        "당신은 전문 데이터 분석가이자 교육 컨설턴트입니다. "
        "학생이 방금 푼 레벨 테스트에서 틀린 문제의 '커리큘럼 카테고리' 리스트를 제공합니다. "
        "이 데이터를 분석하여 학생의 가장 큰 취약점 1~2개를 진단하고, "
        "다음 학습을 위해 어떤 토픽을 공부해야 할지 3문장으로 요약해주세요."
    )