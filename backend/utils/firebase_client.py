import os
import firebase_admin
from firebase_admin import credentials, firestore
from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

def initialize_firebase():
    """Firebase Admin SDK 초기화 및 Firestore 클라이언트 반환"""
    try:
        # Cloud Run 환경 체크
        if os.environ.get('K_SERVICE'):
            logger.info("Cloud Run 환경 감지 - ADC 사용")
            firebase_admin.initialize_app(options={'projectId': Config.PROJECT_ID})
        else:
            # 로컬 환경
            if os.path.exists(Config.SERVICE_ACCOUNT_KEY):
                logger.info(f"로컬 환경 - 서비스 계정 키 사용: {Config.SERVICE_ACCOUNT_KEY}")
                cred = credentials.Certificate(Config.SERVICE_ACCOUNT_KEY)
                firebase_admin.initialize_app(cred, options={'projectId': Config.PROJECT_ID})
            else:
                logger.warning("서비스 계정 키 없음 - 로컬 ADC 시도")
                firebase_admin.initialize_app(options={'projectId': Config.PROJECT_ID})
        
        db = firestore.client()
        logger.info("Firebase 초기화 성공")
        return db
        
    except Exception as e:
        logger.error(f"Firebase 초기화 실패: {e}", exc_info=True)
        return None