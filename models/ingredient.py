"""
성분 모델
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Ingredient(Base):
    """성분 테이블 모델"""
    __tablename__ = 'ingredients'

    id = Column(Integer, primary_key=True, autoincrement=True)
    food_id = Column(Integer, ForeignKey('foods.id'), nullable=False, index=True)
    rank = Column(Integer, nullable=False)          # 원료 순서
    name = Column(String(255), nullable=False, index=True)  # 원료명

    # 분류 태그
    is_grain = Column(Boolean, default=False, index=True)       # 곡물 여부
    is_byproduct = Column(Boolean, default=False, index=True) # 부산물 여부
    is_meat = Column(Boolean, default=False)                   # 고기/생선 여부
    is_synthetic = Column(Boolean, default=False, index=True)  # 합성 첨가물 여부
    is_preservative = Column(Boolean, default=False)            # 방부제 여부
    is_coloring = Column(Boolean, default=False)               # 인공 색소 여부
    is_flavor = Column(Boolean, default=False)                 # 인공 향료 여부

    # 추가 정보
    percentage = Column(Float)             # 비율 (있는 경우)
    description = Column(String(500))       # 상세 설명
    source = Column(String(100))           # 출처 (예: 닭고기, 연어)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Ingredient(id={self.id}, food_id={self.food_id}, rank={self.rank}, name='{self.name}')>"
