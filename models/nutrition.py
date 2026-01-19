"""
영양 성분 모델
"""
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Nutrition(Base):
    """영양 성분 테이블 모델"""
    __tablename__ = 'nutrition'

    id = Column(Integer, primary_key=True, autoincrement=True)
    food_id = Column(Integer, ForeignKey('foods.id'), nullable=False, unique=True, index=True)

    # 보장성분 (Guaranteed Analysis)
    protein = Column(Float)        # 단백질 %
    fat = Column(Float)            # 지방 %
    fiber = Column(Float)          # 섬유소 %
    moisture = Column(Float)       # 수분 %
    ash = Column(Float)            # 회분 %
    carbs = Column(Float)          # 탄수화물 % (계산값)

    # 추가 영양 정보
    calories = Column(Float)       # 칼로리 (kcal/100g 또는 kcal/cup)
    calcium = Column(Float)        # 칼슘 %
    phosphorus = Column(Float)     # 인 %
    taurine = Column(Float)        # 타우린 %
    omega_3 = Column(Float)        # 오메가-3 %
    omega_6 = Column(Float)       # 오메가-6 %

    # 메타데이터
    source_url = Column(Text)      # 데이터 출처 URL
    data_type = Column(String(50))  # 'raw', 'dry_matter', 'as_fed'

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Nutrition(id={self.id}, food_id={self.food_id}, protein={self.protein}%)>"
