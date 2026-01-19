"""
데이터베이스 마이그레이션 스크립트 (SQLite 버전)
"""
from sqlalchemy import text
from database.connection_sqlite import db
from config.settings import log_config
import logging

logging.basicConfig(level=log_config.level, format=log_config.format)
logger = logging.getLogger(__name__)


def create_tables():
    """모든 테이블 생성"""
    try:
        # 모델 임포트
        from models.brand import Base as BrandBase
        from models.food import Base as FoodBase
        from models.nutrition import Base as NutritionBase
        from models.ingredient import Base as IngredientBase

        # 테이블 생성
        BrandBase.metadata.create_all(bind=db.engine)
        FoodBase.metadata.create_all(bind=db.engine)
        NutritionBase.metadata.create_all(bind=db.engine)
        IngredientBase.metadata.create_all(bind=db.engine)

        logger.info("모든 테이블 생성 완료")

    except Exception as e:
        logger.error(f"테이블 생성 실패: {e}")
        raise


def drop_tables():
    """모든 테이블 삭제 (주의사용)"""
    try:
        from models.brand import Base as BrandBase
        from models.food import Base as FoodBase
        from models.nutrition import Base as NutritionBase
        from models.ingredient import Base as IngredientBase

        # 테이블 삭제
        IngredientBase.metadata.drop_all(bind=db.engine)
        NutritionBase.metadata.drop_all(bind=db.engine)
        FoodBase.metadata.drop_all(bind=db.engine)
        BrandBase.metadata.drop_all(bind=db.engine)

        logger.info("모든 테이블 삭제 완료")

    except Exception as e:
        logger.error(f"테이블 삭제 실패: {e}")
        raise


if __name__ == '__main__':
    # 데이터베이스 연결
    db.connect()

    # 테이블 생성
    create_tables()

    # 연결 종료
    db.disconnect()
