"""
네이버 쇼핑 API 클라이언트
"""
import time
import requests
import os
import json
from typing import List, Dict, Optional
from config.settings import log_config
import logging

logging.basicConfig(level=log_config.level, format=log_config.format)
logger = logging.getLogger(__name__)


def load_brands(filepath: str = "brands.json") -> Dict:
    """
    brands.json 로드

    Args:
        filepath: brands.json 파일 경로

    Returns:
        브랜드 딕셔너리
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        logger.warning(f"brands.json을 찾을 수 없습니다: {filepath}")
        return {"brands": {}, "last_updated": None, "version": "1.0"}
    except json.JSONDecodeError as e:
        logger.error(f"brands.json 파싱 오류: {e}")
        return {"brands": {}, "last_updated": None, "version": "1.0"}


def save_brands(data: Dict, filepath: str = "brands.json"):
    """
    brands.json 저장

    Args:
        data: 브랜드 딕셔너리
        filepath: brands.json 파일 경로
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"브랜드 사전이 저장되었습니다: {filepath}")
    except Exception as e:
        logger.error(f"brands.json 저장 오류: {e}")


class NaverShoppingAPI:
    """네이버 쇼핑 검색 API 클라이언트"""

    def __init__(self):
        self.client_id = os.environ.get('NAVER_CLIENT_ID')
        self.client_secret = os.environ.get('NAVER_CLIENT_SECRET')
        self.search_url = "https://openapi.naver.com/v1/search/shop.json"
        self.headers = {
            'X-Naver-Client-Id': self.client_id,
            'X-Naver-Client-Secret': self.client_secret
        }

        # 브랜드 그룹 로드
        brands_data = load_brands()
        self.brand_groups = brands_data.get('brands', {})
        self.category_id = brands_data.get('category_id', '50006679')
        self.single_word_brands = brands_data.get('single_word_brands', [])

    def generate_query(self, brand: str, group: str, manufacturer: str = None) -> str:
        """
        브랜드 그룹에 따른 검색어 생성

        Args:
            brand: 브랜드명
            group: 브랜드 그룹 (standalone, domestic, asia, prescription)
            manufacturer: 제조사 (with_manufacturer 그룹에서 사용)

        Returns:
            생성된 검색어
        """
        # Case 1: 단독 검색 (대부분의 프리미엄 브랜드)
        if group in ['standalone', 'overseas_premium', 'domestic', 'asia', 'prescription']:
            return f"{brand} 사료"

        # Case 2: 제조사 + 브랜드
        elif manufacturer:
            return f"{manufacturer} {brand} 사료"

        # Case 3: 일반명사 보정 (GO!, Now Fresh 등 단어 기반 브랜드)
        elif group == 'general_name_correction' or brand in self.single_word_brands:
            return f"고양이 사료 {brand}"

        # Default: 브랜드명 + 사료
        else:
            return f"{brand} 사료"

    def search(
        self,
        query: str,
        display: int = 10,
        start: int = 1,
        sort: str = 'sim',
        exclude: Optional[str] = None
    ) -> List[Dict]:
        """
        네이버 쇼핑 검색 API 호출

        Args:
            query: 검색어
            display: 한 페이지에 보여질 결과 수 (최대 100)
            start: 검색 시작 위치 (최대 1000)
            sort: 정렬 옵션 (sim: 유사도순, date: 날짜순, asc: 가격 오름차순, dsc: 가격 내림차순)
            exclude: 제외 상품 카테고리

        Returns:
            상품 리스트
        """
        if not self.client_id or not self.client_secret:
            logger.error("네이버 API 인증 정보가 설정되지 않았습니다.")
            raise ValueError("NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET이 필요합니다.")

        params = {
            'query': query,
            'display': display,
            'start': start,
            'sort': sort
        }

        if exclude:
            params['exclude'] = exclude

        try:
            response = requests.get(
                self.search_url,
                headers=self.headers,
                params=params
            )
            response.raise_for_status()

            data = response.json()

            if 'items' in data:
                return data['items']
            else:
                logger.warning(f"검색 결과가 없습니다. query={query}")
                return []

        except requests.exceptions.RequestException as e:
            logger.error(f"네이버 API 요청 실패: {e}")
            return []

    def fetch_all_cat_foods(
        self,
        max_results: int = 1000,
        batch_size: int = 100,
        query: str = "고양이 사료"
    ) -> List[Dict]:
        """
        고양이 사료 검색 결과를 모두 가져옵니다.

        Args:
            max_results: 최대 결과 수
            batch_size: 한 번에 가져올 결과 수
            query: 검색어

        Returns:
            모든 상품 리스트
        """
        all_items = []
        total_fetched = 0

        while total_fetched < max_results:
            remaining = min(batch_size, max_results - total_fetched)
            start = total_fetched + 1

            items = self.search(
                query=query,
                display=remaining,
                start=start,
                sort='sim'  # 유사도순 정렬 (인기 상품 우선)
            )

            if not items:
                break

            all_items.extend(items)
            total_fetched += len(items)

            logger.info(f"{total_fetched}/{max_results} 개 상품 수집 완료")

            # 요청 간 딜레이
            time.sleep(0.5)

        logger.info(f"총 {len(all_items)} 개 상품 수집 완료")
        return all_items

    def extract_food_info(self, item: Dict) -> Dict:
        """
        네이버 API 응답에서 사료 정보를 추출합니다.

        Args:
            item: 네이버 API 상품 아이템

        Returns:
            추출된 사료 정보 딕셔너리
        """
        return {
            'naver_product_id': item.get('productId'),
            'name': item.get('title', '').replace('<b>', '').replace('</b>', ''),
            'link': item.get('link'),
            'image': item.get('image'),
            'min_price': float(item.get('lprice', 0)) if item.get('lprice') else None,
            'max_price': float(item.get('hprice', 0)) if item.get('hprice') else None,
            'mall_name': item.get('mallName'),
            'product_type': item.get('productType'),  # 1: 도서, 2: 쇼핑몰, 3: 티켓
            'maker': item.get('maker'),  # 제조사
            'brand': item.get('brand'),  # 브랜드
            'category1': item.get('category1'),
            'category2': item.get('category2'),
            'category3': item.get('category3'),
            'category4': item.get('category4')
        }

    def filter_by_product_type(self, items: List[Dict], product_type: int = 2) -> List[Dict]:
        """
        productType으로 필터링 (2: 가격비교/카탈로그 상품 우선)

        Args:
            items: 상품 리스트
            product_type: 필터링할 productType (기본: 2)

        Returns:
            필터링된 상품 리스트
        """
        return [item for item in items if item.get('productType') == product_type]

    def track_a_brand_search(
        self,
        brands_data: Dict,
        max_results_per_brand: int = 100
    ) -> List[Dict]:
        """
        Track A: 브랜드 기반 검색 (그룹화 전략 적용)

        Args:
            brands_data: 브랜드 데이터 (그룹 포함)
            max_results_per_brand: 브랜드당 최대 결과 수

        Returns:
            수집된 상품 리스트
        """
        all_items = []
        processed_brands = set()

        # 1. 단독 검색 그룹 (overseas_premium, domestic, asia, prescription)
        for group_key in ['overseas_premium', 'domestic', 'asia', 'prescription']:
            brands = brands_data.get(group_key, [])
            if not brands:
                continue

            logger.info(f"Track A: {group_key} 그룹 검색 시작 ({len(brands)}개)")

            for brand in brands:
                if brand in processed_brands:
                    continue
                processed_brands.add(brand)

                query = self.generate_query(brand, group_key)
                logger.info(f"  검색: {query}")

                items = self.fetch_all_cat_foods(
                    max_results=max_results_per_brand,
                    query=query
                )

                if items:
                    # 카테고리 필터링 (사후 필터링)
                    filtered_items = self.filter_by_category(items)

                    # 가격비교(Type 2) 카탈로그 상품 필터링
                    type_filtered_items = self.filter_by_product_type(filtered_items, product_type=2)

                    # 카탈로그 상품이 하나도 없으면 예외적으로 전체 상품 사용
                    if not type_filtered_items and filtered_items:
                        logger.warning(f"  ⚠️  {brand}: 카탈로그 상품(Type 2) 없음, 전체 상품 사용")
                        type_filtered_items = filtered_items

                    all_items.extend(type_filtered_items)
                    logger.info(f"    → {len(type_filtered_items)}개 수집 완료 (원본: {len(items)}개, 카테고리: {len(filtered_items)}개, Type 2: {len(type_filtered_items)}개)")

        # 2. 제조사 + 브랜드 그룹
        manufacturer_pairs = brands_data.get('manufacturer_brand_pairs', [])
        if manufacturer_pairs:
            logger.info(f"Track A: 제조사+브랜드 그룹 검색 시작")

            for pair in manufacturer_pairs:
                manufacturer = pair.get('manufacturer')
                brands = pair.get('brands', [])

                for brand in brands:
                    if brand in processed_brands:
                        continue
                    processed_brands.add(brand)

                    query = self.generate_query(brand, 'with_manufacturer', manufacturer)
                    logger.info(f"  검색: {query}")

                    items = self.fetch_all_cat_foods(
                        max_results=max_results_per_brand,
                        query=query
                    )

                    if items:
                        # 카테고리 필터링 (사후 필터링)
                        filtered_items = self.filter_by_category(items)

                        # 가격비교(Type 2) 카탈로그 상품 필터링
                        type_filtered_items = self.filter_by_product_type(filtered_items, product_type=2)

                        # 카탈로그 상품이 하나도 없으면 예외적으로 전체 상품 사용
                        if not type_filtered_items and filtered_items:
                            logger.warning(f"  ⚠️  {brand}: 카탈로그 상품(Type 2) 없음, 전체 상품 사용")
                            type_filtered_items = filtered_items

                        all_items.extend(type_filtered_items)
                        logger.info(f"    → {len(type_filtered_items)}개 수집 완료 (원본: {len(items)}개, 카테고리: {len(filtered_items)}개, Type 2: {len(type_filtered_items)}개)")

        # 3. 일반명사 보정 그룹 (단어 기반 브랜드)
        general_brands = brands_data.get('general_name_correction', [])
        if general_brands:
            logger.info(f"Track A: 일반명사 보정 그룹 검색 시작 ({len(general_brands)}개)")

            for brand in general_brands:
                if brand in processed_brands:
                    continue
                processed_brands.add(brand)

                query = self.generate_query(brand, 'general_name_correction')
                logger.info(f"  검색: {query}")

                items = self.fetch_all_cat_foods(
                    max_results=max_results_per_brand,
                    query=query
                )

                if items:
                    # 카테고리 필터링 (사후 필터링)
                    filtered_items = self.filter_by_category(items)

                    # 가격비교(Type 2) 카탈로그 상품 필터링
                    type_filtered_items = self.filter_by_product_type(filtered_items, product_type=2)

                    # 카탈로그 상품이 하나도 없으면 예외적으로 전체 상품 사용
                    if not type_filtered_items and filtered_items:
                        logger.warning(f"  ⚠️  {brand}: 카탈로그 상품(Type 2) 없음, 전체 상품 사용")
                        type_filtered_items = filtered_items

                    all_items.extend(type_filtered_items)
                    logger.info(f"    → {len(type_filtered_items)}개 수집 완료 (원본: {len(items)}개, 카테고리: {len(filtered_items)}개, Type 2: {len(type_filtered_items)}개)")

        return all_items

    def track_b_category_price_range(
        self,
        base_query: str = "고양이 사료",
        max_results_per_range: int = 100
    ) -> List[Dict]:
        """
        Track B: 카테고리 기반 가격대 슬라이싱

        가격대:
        - 저가: 0 ~ 30,000원
        - 중가: 30,000 ~ 70,000원
        - 고가: 70,000원 이상

        Args:
            base_query: 기본 검색어
            max_results_per_range: 가격대별 최대 결과 수

        Returns:
            수집된 상품 리스트
        """
        all_items = []

        # 가격대별 검색 (asc: 가격 오름차순, dsc: 가격 내림차순)
        price_ranges = [
            (0, 30000, 'asc'),   # 저가
            (30000, 70000, 'asc'), # 중가
            (70000, float('inf'), 'dsc')  # 고가
        ]

        for min_price, max_price, sort in price_ranges:
            query = f"{base_query}"
            logger.info(f"Track B: 가격대 검색 - {min_price:,}~{max_price if max_price != float('inf') else max_price:,}원")

            # 가격대별 수집 (API는 직접 가격 필터링 없음, sort만 사용 가능)
            items = self.fetch_all_cat_foods(
                max_results=max_results_per_range,
                query=query
            )

            # 카테고리 필터링 (사후 필터링)
            category_filtered_items = self.filter_by_category(items)

            # 가격비교(Type 2) 카탈로그 상품 필터링
            type_filtered_items = self.filter_by_product_type(category_filtered_items, product_type=2)

            # 카탈로그 상품이 하나도 없으면 예외적으로 전체 상품 사용
            if not type_filtered_items and category_filtered_items:
                logger.warning(f"  ⚠️  가격대 {min_price:,}~{max_price:,}원: 카탈로그 상품(Type 2) 없음, 전체 상품 사용")
                type_filtered_items = category_filtered_items

            # 가격대 필터링
            price_filtered_items = []
            for item in type_filtered_items:
                lprice = int(item.get('lprice', 0))
                if min_price <= lprice < max_price:
                    price_filtered_items.append(item)

            if price_filtered_items:
                all_items.extend(price_filtered_items)
                logger.info(f"  → {len(price_filtered_items)}개 수집 완료 (원본: {len(items)}개, 카테고리: {len(category_filtered_items)}개, Type 2: {len(type_filtered_items)}개)")

        return all_items

    def track_c_discover_new_brands(
        self,
        existing_brands: set,
        items: List[Dict]
    ) -> List[str]:
        """
        Track C: 신규 브랜드 자동 발견

        Args:
            existing_brands: 기존 브랜드 세트
            items: 분석할 상품 리스트

        Returns:
            발견된 신규 브랜드 리스트
        """
        new_brands = []

        if not existing_brands:
            existing_brands = set()

        for item in items:
            brand = item.get('brand', '').strip()
            if brand and brand not in existing_brands:
                new_brands.append(brand)
                existing_brands.add(brand)
                logger.info(f"  🆕 신규 브랜드 발견: {brand}")

        return list(set(new_brands))  # 중복 제거

    def deduplicate_by_product_id(self, items: List[Dict]) -> List[Dict]:
        """
        productId 기반 중복 제거

        Args:
            items: 상품 리스트

        Returns:
            중복 제거된 상품 리스트
        """
        seen_ids = set()
        unique_items = []

        for item in items:
            product_id = item.get('productId')
            if product_id and product_id not in seen_ids:
                seen_ids.add(product_id)
                unique_items.append(item)

        removed_count = len(items) - len(unique_items)
        if removed_count > 0:
            logger.info(f"  🔄 PID 중복 제거: {removed_count}개 제거됨")

        return unique_items

    def filter_by_category(self, items: List[Dict]) -> List[Dict]:
        """
        카테고리 기반 필터링 (Post-Filtering)
        category3 또는 category4에 '사료'가 포함된 것만 추출

        네이버 API는 카테고리 필터를 지원하지 않으므로,
        응답 결과물에서 필터링하는 방식을 사용합니다.

        Args:
            items: 상품 리스트

        Returns:
            필터링된 상품 리스트
        """
        filtered_items = []
        for item in items:
            category3 = item.get('category3', '')
            category4 = item.get('category4', '')

            # category3이나 category4에 '사료'가 포함되어 있는지 확인
            if '사료' in category3 or '사료' in category4:
                filtered_items.append(item)
            # 카테고리 ID 기반 필터링 (백업)
            elif ('50006679' in category3 or '50006679' in category4 or
                  '50006679' in item.get('category2', '') or
                  '50006679' in item.get('category1', '')):
                filtered_items.append(item)

        removed_count = len(items) - len(filtered_items)
        if removed_count > 0:
            logger.info(f"  🏷️  카테고리 필터링: {removed_count}개 제거됨 (비사료 제거)")

        return filtered_items


if __name__ == '__main__':
    # 테스트 코드
    api = NaverShoppingAPI()

    # 검색 테스트
    results = api.search("고양이 사료", display=5)
    print(f"검색 결과: {len(results)} 개")

    if results:
        for item in results:
            info = api.extract_food_info(item)
            print(f"\n상품명: {info['name']}")
            print(f"브랜드: {info['brand']}")
            print(f"가격: {info['min_price']} ~ {info['max_price']} 원")
            print(f"링크: {info['link']}")
