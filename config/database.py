"""
데이터베이스 설정 모듈
"""
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    """데이터베이스 설정 클래스"""

    def __init__(self):
        self.database_url = os.getenv(
            'DATABASE_URL',
            'postgresql://postgres:password@localhost:5432/cat_data_db'
        )

    @property
    def url(self) -> str:
        """데이터베이스 URL 반환"""
        return self.database_url


class NaverAPIConfig:
    """네이버 API 설정 클래스"""

    def __init__(self):
        self.client_id = os.getenv('NAVER_CLIENT_ID', '')
        self.client_secret = os.getenv('NAVER_CLIENT_SECRET', '')
        self.search_api_url = os.getenv(
            'NAVER_SEARCH_API_URL',
            'https://openapi.naver.com/v1/search/shop.json'
        )

    @property
    def headers(self) -> dict:
        """API 요청 헤더 반환"""
        return {
            'X-Naver-Client-Id': self.client_id,
            'X-Naver-Client-Secret': self.client_secret
        }


class LogConfig:
    """로그 설정 클래스"""

    def __init__(self):
        self.level = os.getenv('LOG_LEVEL', 'INFO')
        self.format = os.getenv(
            'LOG_FORMAT',
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )


class FetchConfig:
    """데이터 수집 설정 클래스"""

    def __init__(self):
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))
        self.request_delay = float(os.getenv('REQUEST_DELAY', '1'))
        self.max_concurrent_requests = int(os.getenv('MAX_CONCURRENT_REQUESTS', '10'))
