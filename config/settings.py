"""
전체 설정 모듈
"""
from .database import DatabaseConfig, NaverAPIConfig, LogConfig, FetchConfig

# 전역 설정 인스턴스
db_config = DatabaseConfig()
naver_api_config = NaverAPIConfig()
log_config = LogConfig()
fetch_config = FetchConfig()

__all__ = [
    'db_config',
    'naver_api_config',
    'log_config',
    'fetch_config'
]
