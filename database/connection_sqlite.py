"""
SQLite 버전 데이터베이스 연결 모듈
설치 불필요, 파일로 DB 생성
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config.settings import log_config
import logging

logging.basicConfig(level=log_config.level, format=log_config.format)
logger = logging.getLogger(__name__)


class DatabaseSQLite:
    """SQLite 데이터베이스 연결 및 세션 관리"""

    def __init__(self):
        self.engine = None
        self.SessionLocal = None

    def connect(self):
        """데이터베이스 연결"""
        try:
            # SQLite 사용 (파일로 DB 생성)
            self.engine = create_engine(
                'sqlite:///cat_data.db',
                echo=False,
                connect_args={"check_same_thread": False}  # SQLite용 설정
            )
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            logger.info("SQLite 데이터베이스 연결 성공: cat_data.db")
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


# 전역 DB 인스턴스 (SQLite)
db = DatabaseSQLite()


def get_db():
    """데이터베이스 세션 의존성 주입"""
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()


if __name__ == '__main__':
    # 테스트 코드
    database = DatabaseSQLite()
    database.connect()
    session = database.get_session()
    print("데이터베이스 연결 테스트 성공")
    database.disconnect()
