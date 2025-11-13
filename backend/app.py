import sys
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from utils.logger import setup_logger
from utils.firebase_client import initialize_firebase
from utils.ai_client import initialize_ai_client
from routes.api_routes import create_api_routes

# 로거 설정
logger = setup_logger(__name__)

def create_app():
    """Flask 애플리케이션 팩토리"""
    
    logger.info("=== AI Math 서버 시작 ===")
    logger.info(f"Python 버전: {sys.version.split()[0]}")
    logger.info(f"프로젝트 ID: {Config.PROJECT_ID}")
    
    # Flask 앱 생성
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # CORS 설정
    allowed_origins = [Config.FRONTEND_URL, Config.WIX_SITE_URL]

    CORS(app, resources={
        r"/get_test_problems": {"origins": allowed_origins},
        r"/submit_and_analyze": {"origins": allowed_origins},
        r"/register_guest": {"origins": allowed_origins},
        r"/guest/*": {"origins": allowed_origins},
        r"/wix_webhook": {"origins": "*"},  # Wix webhook은 모든 origin 허용
        r"/wix_velo_sync": {"origins": "*"},  # Wix Velo Backend는 모든 origin 허용
        r"/wix_login": {"origins": allowed_origins},
        r"/user/*": {"origins": allowed_origins}
    })
    logger.info(f"CORS 설정 완료 - Origins: {allowed_origins}")
    
    # Firebase 초기화
    db = initialize_firebase()
    if not db:
        logger.error("Firebase 초기화 실패 - 서버를 시작할 수 없습니다.")
        sys.exit(1)
    
    # AI 클라이언트 초기화
    ai_client = initialize_ai_client()
    if not ai_client:
        logger.error("AI 클라이언트 초기화 실패 - 서버를 시작할 수 없습니다.")
        sys.exit(1)
    
    # API 라우트 등록
    api_bp = create_api_routes(db, ai_client)
    app.register_blueprint(api_bp)
    logger.info("API 라우트 등록 완료")
    
    # 헬스 체크 엔드포인트
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'firebase': db is not None,
            'ai_client': ai_client is not None
        }), 200
    
    # 에러 핸들러
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': '요청한 리소스를 찾을 수 없습니다.'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"서버 내부 오류: {error}")
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500
    
    logger.info("=== 서버 초기화 완료 ===")
    
    return app

# 애플리케이션 인스턴스 생성
app = create_app()

if __name__ == "__main__":
    logger.info(f"개발 서버 시작 - 포트: {Config.PORT}")
    app.run(
        debug=Config.DEBUG,
        host="0.0.0.0",
        port=Config.PORT
    )