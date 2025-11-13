"""
Firebase 인증 미들웨어
"""
from firebase_admin import auth
from functools import wraps
from flask import request, jsonify
from utils.logger import setup_logger

logger = setup_logger(__name__)


def verify_firebase_token(f):
    """
    Firebase ID Token 검증 데코레이터

    Usage:
        @api_bp.route('/protected', methods=['GET'])
        @verify_firebase_token
        def protected_route():
            user_id = request.user_id  # 미들웨어에서 추가된 user_id
            return jsonify({'user_id': user_id})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Authorization 헤더에서 토큰 추출
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            logger.warning("인증 토큰이 없습니다.")
            return jsonify({'error': '인증 토큰이 없습니다.'}), 401

        id_token = auth_header.split('Bearer ')[1]

        try:
            # Firebase Admin SDK로 토큰 검증
            decoded_token = auth.verify_id_token(id_token)
            request.user_id = decoded_token['uid']  # Flask request에 user_id 추가
            logger.info(f"✓ 인증 성공 - User ID: {request.user_id}")
            return f(*args, **kwargs)

        except auth.InvalidIdTokenError:
            logger.error("유효하지 않은 토큰입니다.")
            return jsonify({'error': '유효하지 않은 토큰입니다.'}), 401

        except auth.ExpiredIdTokenError:
            logger.error("만료된 토큰입니다.")
            return jsonify({'error': '만료된 토큰입니다.'}), 401

        except Exception as e:
            logger.error(f"인증 실패: {e}", exc_info=True)
            return jsonify({'error': f'인증 실패: {str(e)}'}), 401

    return decorated_function
