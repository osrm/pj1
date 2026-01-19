"""
로깅 유틸리티
"""
import logging
from colorlog import ColoredFormatter
from config.settings import log_config


def setup_logger(name: str) -> logging.Logger:
    """
    컬러 로거 설정

    Args:
        name: 로거 이름

    Returns:
        설정된 로거 인스턴스
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_config.level))

    # 핸들러가 없으면 추가
    if not logger.handlers:
        handler = logging.StreamHandler()

        # 컬러 포맷 설정
        formatter = ColoredFormatter(
            '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
