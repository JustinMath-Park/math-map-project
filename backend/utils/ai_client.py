from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel
import vertexai
from config import Config
from utils.logger import setup_logger
import time

logger = setup_logger(__name__)

def initialize_ai_client():
    """Vertex AI 클라이언트 초기화 및 반환"""
    try:
        # Vertex AI 초기화
        vertexai.init(
            project=Config.PROJECT_ID,
            location=Config.AI_LOCATION
        )

        # 모델 초기화
        model = GenerativeModel(Config.MODEL_FLASH)

        logger.info(f"AI 클라이언트 초기화 성공 (모델: {Config.MODEL_FLASH})")
        return model

    except Exception as e:
        logger.error(f"AI 클라이언트 초기화 실패: {e}", exc_info=True)
        return None

def call_ai_with_retry(model, contents, max_retries=3):
    """
    AI API 호출 with 재시도 로직

    Args:
        model: Vertex AI 모델
        contents: 프롬프트 내용 (str 또는 list)
        max_retries: 최대 재시도 횟수

    Returns:
        AI 응답 또는 None
    """
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"AI API 호출 시도 {attempt}/{max_retries}")

            response = model.generate_content(contents)

            if response and hasattr(response, 'text') and response.text:
                logger.info(f"AI API 호출 성공 (시도 {attempt}/{max_retries})")
                return response
            else:
                logger.warning(f"AI 응답이 비어있음 (시도 {attempt}/{max_retries})")
                last_error = Exception("Empty AI response")

        except Exception as e:
            logger.error(f"AI API 호출 실패 (시도 {attempt}/{max_retries}): {e}", exc_info=True)

            # 클라이언트 에러는 재시도하지 않음
            if "400" in str(e) or "invalid" in str(e).lower():
                logger.error("클라이언트 에러 - 재시도 중단")
                return None

            last_error = e

        # 마지막 시도가 아니면 재시도 전 대기
        if attempt < max_retries:
            wait_time = min(2 ** attempt, 10)  # 지수 백오프 (최대 10초)
            logger.info(f"⏳ {wait_time}초 후 재시도...")
            time.sleep(wait_time)

    # 모든 재시도 실패
    logger.error(f"AI API 호출 최종 실패 - 모든 재시도 소진. 마지막 에러: {last_error}")
    return None
