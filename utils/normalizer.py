"""
텍스트 정규화 유틸리티
"""
import re
import unicodedata
from typing import Optional
from fetchers.naver_api import load_brands
import logging

logger = logging.getLogger(__name__)


class TextNormalizer:
    """텍스트 정규화 클래스"""

    def __init__(self):
        brands_data_full = load_brands()
        brands_data = brands_data_full.get('brands', {})

        # 모든 브랜드를 단일 리스트로 변환
        self.brand_list = []
        for group_key, group_data in brands_data.items():
            if isinstance(group_data, list):
                if group_data and isinstance(group_data[0], dict):
                    # manufacturer_brand_pairs
                    for pair in group_data:
                        self.brand_list.extend(pair.get('brands', []))
                else:
                    # 일반 리스트
                    self.brand_list.extend(group_data)

        self.brand_set = set(self.brand_list)

    def normalize_text(self, text: str) -> str:
        """
        기본 텍스트 정규화

        Args:
            text: 입력 텍스트

        Returns:
            정규화된 텍스트
        """
        if not text:
            return ""

        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)

        # 공백 정규화 (여러 공백 → 단일 공백)
        text = re.sub(r'\s+', ' ', text)

        # 앞뒤 공백 제거
        text = text.strip()

        # 유니코드 정규화 (NFC)
        text = unicodedata.normalize('NFC', text)

        return text

    def normalize_brand(self, brand: Optional[str]) -> Optional[str]:
        """
        브랜드명 정규화

        Args:
            brand: 브랜드명

        Returns:
            정규화된 브랜드명
        """
        if not brand:
            return None

        brand = self.normalize_text(brand)

        # 대소문자 구분 없이 매칭 (영문 브랜드)
        brand_lower = brand.lower()

        # 브랜드 리스트와 매칭
        for brand_candidate in self.brand_list:
            candidate_lower = brand_candidate.lower()

            # 정확히 일치
            if brand_lower == candidate_lower:
                return brand_candidate

            # 포함 관계 체크
            if brand_lower in candidate_lower or candidate_lower in brand_lower:
                return brand_candidate

        # 브랜드 리스트에 없으면 그대로 반환
        return brand if brand else None

    def normalize_product_name(self, name: str) -> str:
        """
        사료명 정규화

        Args:
            name: 사료명

        Returns:
            정규화된 사료명
        """
        name = self.normalize_text(name)

        # 특수 문자 정규화
        name = re.sub(r'[()]', '', name)  # 괄호 제거
        name = re.sub(r'[\[\]]', '', name)  # 대괄호 제거
        name = re.sub(r'[{}]', '', name)  # 중괄호 제거

        # 상수정보 제거 (배송, 이벤트 등)
        noise_patterns = [
            r'무료배송',
            r'무료배송\?',
            r'오늘출발',
            r'당일발송',
            r'이벤트특가',
            r'한정판매',
            r'최저가',
            r'할인',
            r'\d+%',
            r'쿠폰',
            r'사은품',
        ]

        for pattern in noise_patterns:
            name = re.sub(pattern, '', name)

        # 공백 정규화 (다시)
        name = re.sub(r'\s+', ' ', name).strip()

        return name

    def normalize_category(self, category: Optional[str]) -> Optional[str]:
        """
        카테고리 정규화

        Args:
            category: 카테고리

        Returns:
            정규화된 카테고리
        """
        if not category:
            return None

        category = self.normalize_text(category)

        # 카테고리 매핑
        category_mapping = {
            '건식': '건식사료',
            '습식': '습식사료',
            '간식': '간식',
            '영양제': '영양제',
            '사료': '사료',
            '건사료': '건식사료',
            '습사료': '습식사료',
        }

        # 정확히 일치
        if category in category_mapping:
            return category_mapping[category]

        # 포함 관계 체크
        for key, value in category_mapping.items():
            if key in category:
                return value

        # 기본값 반환
        return category

    def extract_brand_from_name(self, name: str) -> Optional[str]:
        """
        사료명에서 브랜드 추출

        Args:
            name: 사료명

        Returns:
            추출된 브랜드명
        """
        name = self.normalize_text(name)
        name_lower = name.lower()

        for brand in self.brand_list:
            brand_lower = brand.lower()

            # 브랜드명이 사료명 앞에 있는 경우
            if name_lower.startswith(brand_lower):
                return brand

            # 브랜드명이 포함된 경우
            if brand_lower in name_lower:
                return brand

        return None

    def normalize_price(self, price_str: str) -> Optional[float]:
        """
        가격 정규화

        Args:
            price_str: 가격 문자열

        Returns:
            정규화된 가격 (float)
        """
        if not price_str:
            return None

        # 숫자 및 콤마만 추출
        price_match = re.search(r'[\d,]+', price_str)

        if price_match:
            price_str = price_match.group()
            price_str = price_str.replace(',', '')
            try:
                return float(price_str)
            except ValueError:
                return None

        return None


# 싱글톤 인스턴스
_normalizer_instance = None


def get_normalizer() -> TextNormalizer:
    """TextNormalizer 싱글톤 인스턴스 반환"""
    global _normalizer_instance
    if _normalizer_instance is None:
        _normalizer_instance = TextNormalizer()
    return _normalizer_instance
