from google import genai
from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

def initialize_ai_client():
    """Google Gen AI 클라이언트 초기화 및 반환"""
    try:
        client = genai.Client(
            vertexai=True,
            project=Config.PROJECT_ID,
            location=Config.AI_LOCATION
        )
        logger.info("AI 클라이언트 초기화 성공")
        return client
        
    except Exception as e:
        logger.error(f"AI 클라이언트 초기화 실패: {e}", exc_info=True)
        return None