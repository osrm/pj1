"""
브랜드 모델
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Brand(Base):
    """브랜드 테이블 모델"""
    __tablename__ = 'brands'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    country = Column(String(50))
    official_url = Column(String(255))
    description = Column(String(500))

    def __repr__(self):
        return f"<Brand(id={self.id}, name='{self.name}', country='{self.country}')>"
