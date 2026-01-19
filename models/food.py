"""
사료 모델
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Food(Base):
    """사료 테이블 모델"""
    __tablename__ = 'foods'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    brand_id = Column(Integer, ForeignKey('brands.id'), nullable=True)
    category = Column(String(50))  # dry, wet, freeze_dried, raw
    type = Column(String(50))      # kitten, adult, senior, weight_control
    size = Column(String(50))      # 사이즈 정보 (예: 1.5kg, 5.4kg)
    price = Column(Float)          # 최저가
    min_price = Column(Float)       # 최저가 (네이버 API)
    max_price = Column(Float)       # 최고가 (네이버 API)
    link = Column(Text)            # 상품 링크 (네이버 API)
    image = Column(Text)           # 상품 이미지 URL
    naver_product_id = Column(String(100), index=True)  # 네이버 상품 ID
    manufacturer = Column(String(100))  # 제조사
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Food(id={self.id}, name='{self.name}', brand_id={self.brand_id})>"
