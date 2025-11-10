import logging
import sys

def setup_logger(name: str, level=logging.INFO):
    """로거 설정 및 반환"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 핸들러가 이미 있으면 추가하지 않음 (중복 방지)
    if logger.handlers:
        return logger
    
    # 콘솔 핸들러
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # 포맷 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    return logger