"""
중복 제거 모듈
naver_product_id 기반 중복 제거
"""
from sqlalchemy.orm import Session
from models.food import Food
from models.brand import Brand
import logging

logger = logging.getLogger(__name__)


class DuplicateRemover:
    """중복 제거 클래스"""

    @staticmethod
    def check_duplicate_by_product_id(session: Session, product_id: str) -> bool:
        """
        naver_product_id 기반 중복 체크

        Args:
            session: DB 세션
            product_id: 네이버 상품 ID

        Returns:
            중복 여부 (True: 중복, False: 중복 아님)
        """
        existing = session.query(Food).filter_by(
            naver_product_id=product_id
        ).first()

        return existing is not None

    @staticmethod
    def check_duplicate_by_name_brand(
        session: Session,
        name: str,
        brand_name: Optional[str] = None
    ) -> bool:
        """
        이름 + 브랜드 기반 중복 체크 (ID가 없는 경우)

        Args:
            session: DB 세션
            name: 사료명
            brand_name: 브랜드명

        Returns:
            중복 여부 (True: 중복, False: 중복 아님)
        """
        if not brand_name:
            return False

        # 브랜드 찾기
        brand = session.query(Brand).filter_by(name=brand_name).first()
        if not brand:
            return False

        # 이름 + 브랜드 기반 체크
        existing = session.query(Food).filter(
            Food.name == name,
            Food.brand_id == brand.id
        ).first()

        return existing is not None

    @staticmethod
    def save_food(
        session: Session,
        product_info: dict,
        brand_id: Optional[int] = None
    ) -> Optional[Food]:
        """
        중복 체크 후 사료 저장

        Args:
            session: DB 세션
            product_info: 상품 정보 딕셔너리
            brand_id: 브랜드 ID

        Returns:
            저장된 Food 모델 또는 None (중복인 경우)
        """
        # 1차: naver_product_id 기반 체크
        if product_info.get('naver_product_id'):
            if DuplicateRemover.check_duplicate_by_product_id(
                session,
                product_info['naver_product_id']
            ):
                logger.debug(f"중복 (ID 기반): {product_info['naver_product_id']}")
                return None

        # 2차: name + brand 기반 체크
        brand_name = product_info.get('brand')
        if DuplicateRemover.check_duplicate_by_name_brand(
            session,
            product_info['name'],
            brand_name
        ):
            logger.debug(f"중복 (이름+브랜드 기반): {product_info['name']} ({brand_name})")
            return None

        # 중복 아니면 저장
        food = Food(
            name=product_info['name'],
            brand_id=brand_id,
            category=None,  # 추후 매칭
            type=None,  # 추후 매칭
            size=None,  # 추후 매칭
            min_price=product_info.get('price'),
            max_price=None,  # 크롤링에는 최저가만
            link=product_info.get('link'),
            image=product_info.get('image'),
            naver_product_id=product_info.get('naver_product_id'),
            manufacturer=None  # 추후 업데이트
        )

        session.add(food)
        session.commit()
        session.refresh(food)

        return food

    @staticmethod
    def get_duplicate_stats(session: Session) -> dict:
        """
        중복 통계

        Args:
            session: DB 세션

        Returns:
            통계 딕셔너리
        """
        total_foods = session.query(Food).count()
        unique_ids = session.query(Food.naver_product_id).filter(
            Food.naver_product_id.isnot(None)
        ).distinct().count()
        no_id_foods = session.query(Food).filter(
            Food.naver_product_id.is_(None)
        ).count()

        return {
            'total_foods': total_foods,
            'unique_ids': unique_ids,
            'no_id_foods': no_id_foods,
            'potential_duplicates': total_foods - unique_ids
        }
