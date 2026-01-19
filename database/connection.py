"""
데이터베이스 연결 모듈
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config.settings import db_config
from config.settings import log_config
import logging

logging.basicConfig(level=log_config.level, format=log_config.format)
logger = logging.getLogger(__name__)


class Database:
    """데이터베이스 연결 및 세션 관리"""

    def __init__(self):
        self.engine = None
        self.SessionLocal = None

    def connect(self):
        """데이터베이스 연결"""
        try:
            self.engine = create_engine(
                db_config.url,
                echo=False,
                pool_pre_ping=True
            )
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            logger.info(f"데이터베이스 연결 성공: {db_config.url}")
        except Exception as e:
            logger.error(f"데이터베이스 연결 실패: {e}")
            raise

    def get_session(self) -> Session:
        """데이터베이스 세션 반환"""
        if not self.SessionLocal:
            raise RuntimeError("데이터베이스가 연결되지 않았습니다.")
        return self.SessionLocal()

    def disconnect(self):
        """데이터베이스 연결 종료"""
        if self.engine:
            self.engine.dispose()
            logger.info("데이터베이스 연결 종료")


# 전역 DB 인스턴스
db = Database()


def get_db():
    """데이터베이스 세션 의존성 주입 (FastAPI 등에서 사용)"""
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()


if __name__ == '__main__':
    # 테스트 코드
    database = Database()
    database.connect()
    session = database.get_session()
    print("데이터베이스 연결 테스트 성공")
    database.disconnect()
