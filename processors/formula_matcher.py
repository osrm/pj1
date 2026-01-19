"""
Formula 방식 매칭 프로세서
네이버 API에서 받아온 제품명을 분석하여 정확한 사료 정보를 매칭합니다.
"""
import re
from typing import Dict, List, Optional
from config.settings import log_config
import logging

logging.basicConfig(level=log_config.level, format=log_config.format)
logger = logging.getLogger(__name__)


class FormulaMatcher:
    """Formula 방식 매칭 클래스"""

    def __init__(self):
        # 브랜드별 키워드 패턴
        self.brand_patterns = {
            '오리젠': r'오리젠|acana|orijen',
            '고이': r'고이|go!',
            '웰니스코어': r'웰니스코어|wellness core',
            '인보스트': r'인보스트|instinct',
            '이존': r'이존|earthborn',
            '솔리드골드': r'솔리드골드|solid gold',
            '캐츠란': r'캐츠란|catz finefood',
            '타워': r'타워|taste of the wild',
            '카니발': r'카니발|carnilove',
            '앱솔루트': r'앱솔루트|animonda',
            '로얄캐닌': r'로얄캐닌|royal canin',
            '힐스': r'힐스|hill\'?s?',
            '퓨리나': r'퓨리나|purina',
            '이즈': r'이즈|i?e?w? s?',
            '스마트하트': r'스마트하트|smartheart',
            '아이엠에스': r'아이엠에스|ims',
            '니베아': r'니베아|nivea',
            '비바': r'비바|biva',
        }

        # 연령별 키워드
        self.age_keywords = {
            'kitten': ['키튼', 'kitten', '새끼', '유아', '어린'],
            'adult': ['성묘', 'adult', '성년'],
            'senior': ['시니어', 'senior', '노령', '노년']
        }

        # 카테고리별 키워드
        self.category_keywords = {
            'dry': ['건식', 'dry'],
            'wet': ['습식', 'wet', '캔', '파우치', 'pouch', '캔슈'],
            'freeze_dried': ['동결건조', '프리즈드라이', 'freeze dried'],
            'raw': ['생식', 'raw', '바']
        }

        # 사이즈 패턴
        self.size_pattern = re.compile(r'(\d+\.?\d*)\s*(kg|g|lb|oz)', re.IGNORECASE)

    def parse_product_name(self, product_name: str) -> Dict:
        """
        제품명에서 브랜드, 연령, 카테고리, 사이즈 정보 추출

        Args:
            product_name: 제품명

        Returns:
            추출된 정보 딕셔너리
        """
        cleaned_name = self._clean_name(product_name)

        result = {
            'name': cleaned_name,
            'brand': self._extract_brand(cleaned_name),
            'age': self._extract_age(cleaned_name),
            'category': self._extract_category(cleaned_name),
            'size': self._extract_size(cleaned_name),
            'type': self._extract_type(cleaned_name)
        }

        return result

    def _clean_name(self, name: str) -> str:
        """제품명 정제"""
        # HTML 태그 제거
        name = re.sub(r'<[^>]+>', '', name)
        # 불필요한 공백 제거
        name = ' '.join(name.split())
        return name.strip()

    def _extract_brand(self, name: str) -> Optional[str]:
        """브랜드 추출"""
        for brand, pattern in self.brand_patterns.items():
            if re.search(pattern, name, re.IGNORECASE):
                return brand
        return None

    def _extract_age(self, name: str) -> Optional[str]:
        """연령 추출"""
        for age, keywords in self.age_keywords.items():
            for keyword in keywords:
                if keyword in name.lower():
                    return age
        return 'adult'  # 기본값: 성묘

    def _extract_category(self, name: str) -> Optional[str]:
        """카테고리 추출"""
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in name.lower():
                    return category
        return 'dry'  # 기본값: 건식

    def _extract_size(self, name: str) -> Optional[str]:
        """사이즈 추출"""
        match = self.size_pattern.search(name)
        if match:
            size = match.group(1)
            unit = match.group(2).lower()
            return f"{size}{unit}"
        return None

    def _extract_type(self, name: str) -> Optional[str]:
        """타입 추출 (다이어트, 관절, 피부 등)"""
        type_keywords = {
            'weight_control': ['다이어트', '체중조절', '체중관리', 'weight control'],
            'joint': ['관절', 'joint'],
            'skin': ['피부', 'skin', '모질'],
            'sensitive': ['저자극', '센서티브', 'sensitive'],
            'hairball': ['헤어볼', '털뭉치', 'hairball'],
            'urinary': ['요로', '비뇨', 'urinary']
        }

        for food_type, keywords in type_keywords.items():
            for keyword in keywords:
                if keyword in name.lower():
                    return food_type

        return None

    def match_with_database(self, product_name: str, existing_foods: List[str]) -> Optional[str]:
        """
        기존 DB에 있는 제품명과 매칭

        Args:
            product_name: 네이버 API에서 받아온 제품명
            existing_foods: DB에 있는 제품명 리스트

        Returns:
            매칭된 제품명 또는 None
        """
        parsed = self.parse_product_name(product_name)

        # 유사도 기반 매칭
        # TODO: 더 정교한 매칭 알고리즘 구현 (Levenshtein distance, N-gram 등)

        return None


if __name__ == '__main__':
    # 테스트 코드
    matcher = FormulaMatcher()

    # 테스트 제품명들
    test_products = [
        "오리젠 고양이 성묘 사료 고양이과 5.4kg",
        "고이 센서티브 + 쉬킨 스킨 앤 코트 5.5kg",
        "웰니스코어 오리얼 치킨 성묘 2.27kg",
        "인보스트 리미티드 다이어트 고양이 3.2kg"
    ]

    for product in test_products:
        result = matcher.parse_product_name(product)
        print(f"\n제품명: {result['name']}")
        print(f"브랜드: {result['brand']}")
        print(f"연령: {result['age']}")
        print(f"카테고리: {result['category']}")
        print(f"사이즈: {result['size']}")
        print(f"타입: {result['type']}")
