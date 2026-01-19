"""
전체 실행 스크립트 (SQLite 버전)
DB 초기화 → 네이버 API로 데이터 수집 → 결과 확인까지 한번에 실행
"""
from database.connection_sqlite import db
from database.migration_sqlite import create_tables, drop_tables
from fetchers.naver_api import NaverShoppingAPI, load_brands, save_brands
from processors.formula_matcher import FormulaMatcher
from models.brand import Brand
from models.food import Food
from utils.normalizer import get_normalizer
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

load_dotenv()


def save_brand(session: Session, brand_name: str) -> Brand:
    """브랜드 저장 (중복 시 기존 브랜드 반환)"""
    brand = session.query(Brand).filter_by(name=brand_name).first()
    if not brand:
        brand = Brand(name=brand_name)
        session.add(brand)
        session.commit()
        session.refresh(brand)
    return brand


def run_all(max_results: int = 100, reset_db: bool = True):
    """
    전체 프로세스 실행 (3-Track 전략)

    Args:
        max_results: 수집할 최대 사료 개수 (브랜드당/가격대당)
        reset_db: DB 초기화 여부
    """
    print("=" * 60)
    print("Cat-Data Lab 전체 실행 (SQLite 버전 - 3-Track)")
    print("=" * 60)

    # 1. DB 연결
    print("\n[1/7] 데이터베이스 연결 중...")
    db.connect()

    try:
        # 2. 테이블 생성
        print(f"[2/7] 테이블 생성 중... (초기화: {reset_db})")
        if reset_db:
            drop_tables()
        create_tables()

        # 3. 브랜드 사전 로드
        print("\n[3/7] 브랜드 사전 로드 중...")
        brands_data_full = load_brands()
        brands_data = brands_data_full.get('brands', {})

        # 브랜드 수 계산 (모든 그룹 합산)
        total_brands = 0
        for group_key, group_data in brands_data.items():
            if isinstance(group_data, list):
                total_brands += len(group_data)
            elif isinstance(group_data, list) and isinstance(group_data[0], dict):
                # manufacturer_brand_pairs
                for pair in group_data:
                    total_brands += len(pair.get('brands', []))

        print(f"   - 총 브랜드 수: {total_brands}개")
        print(f"   - 그룹 수: {len(brands_data)}개")

        # 모든 브랜드를 단일 리스트로 변환 (기존 호환성 유지)
        all_brands_list = []
        for group_key, group_data in brands_data.items():
            if isinstance(group_data, list):
                if group_data and isinstance(group_data[0], dict):
                    # manufacturer_brand_pairs
                    for pair in group_data:
                        all_brands_list.extend(pair.get('brands', []))
                else:
                    # 일반 리스트
                    all_brands_list.extend(group_data)

        # 텍스트 정규화 초기화
        print("\n[4/7] 텍스트 정규화 초기화 중...")
        normalizer = get_normalizer()
        print(f"   - 브랜드 사전 로드 완료")

        # 5. 3-Track 데이터 수집
        print(f"\n[5/7] 3-Track 데이터 수집 중...")
        api = NaverShoppingAPI()
        matcher = FormulaMatcher()

        all_items = []
        existing_brands = set(all_brands_list)

        # Track A: 브랜드 기반 검색 (그룹화 전략 적용)
        print("\n   Track A: 브랜드 기반 검색 (그룹화 전략)")
        track_a_items = api.track_a_brand_search(
            brands_data=brands_data,
            max_results_per_brand=max_results
        )
        all_items.extend(track_a_items)
        print(f"   → Track A 완료: {len(track_a_items)}개")

        # Track B: 카테고리 기반 가격대 슬라이싱
        print("\n   Track B: 카테고리 기반 가격대 슬라이싱")
        track_b_items = api.track_b_category_price_range(
            max_results_per_range=max_results
        )
        all_items.extend(track_b_items)
        print(f"   → Track B 완료: {len(track_b_items)}개")

        # PID 중복 제거
        print("\n   중복 제거 중...")
        all_items = api.deduplicate_by_product_id(all_items)
        print(f"   → 중복 제거 완료: {len(all_items)}개")

        # Track C: 신규 브랜드 발견
        print("\n   Track C: 신규 브랜드 발견")
        new_brands = api.track_c_discover_new_brands(
            existing_brands=existing_brands,
            items=all_items
        )

        # productType 필터링 (2: 가격비교/카탈로그 상품 우선)
        print("\n   productType 필터링 중...")
        filtered_items = api.filter_by_product_type(all_items, product_type=2)
        print(f"   → 필터링 완료: {len(filtered_items)}개")

        # 신규 브랜드가 있으면 brands.json 업데이트
        if new_brands:
            print(f"\n   신규 브랜드 {len(new_brands)}개 발견 - brands.json 업데이트")
            # 신규 브랜드를 domestic 그룹에 추가 (기본값)
            if 'domestic' not in brands_data:
                brands_data['domestic'] = []
            brands_data['domestic'].extend(new_brands)
            brands_data['domestic'] = sorted(list(set(brands_data['domestic'])))

            brands_data_full['brands'] = brands_data
            brands_data_full['last_updated'] = os.path.getmtime('brands.json') if os.path.exists('brands.json') else None
            save_brands(brands_data_full)

        if not filtered_items:
            print("❌ 필터링 후 수집된 데이터가 없습니다.")
            return

        # 6. 데이터베이스에 저장
        print(f"\n[6/7] 데이터베이스에 저장 중...")
        session = db.get_session()
        saved_count = 0
        skipped_count = 0

        for item in filtered_items:
            try:
                # 사료 정보 추출
                food_info = api.extract_food_info(item)

                # 텍스트 정규화
                food_info['name'] = normalizer.normalize_product_name(food_info['name'])
                food_info['brand'] = normalizer.normalize_brand(food_info['brand'])
                food_info['maker'] = normalizer.normalize_text(food_info['maker'])

                # Formula 방식 매칭
                parsed = matcher.parse_product_name(food_info['name'])

                # 브랜드 정규화 결과 반영
                if food_info['brand'] and not parsed['brand']:
                    parsed['brand'] = food_info['brand']

                # 중복 체크
                existing = session.query(Food).filter_by(
                    naver_product_id=food_info['naver_product_id']
                ).first()

                if existing:
                    skipped_count += 1
                    continue

                # 브랜드 저장
                brand = None
                if parsed['brand']:
                    brand = save_brand(session, parsed['brand'])

                # 사료 저장
                food = Food(
                    name=parsed['name'],
                    brand_id=brand.id if brand else None,
                    category=parsed['category'],
                    type=parsed['age'],
                    size=parsed['size'],
                    min_price=food_info['min_price'],
                    max_price=food_info['max_price'],
                    link=food_info['link'],
                    image=food_info['image'],
                    naver_product_id=food_info['naver_product_id'],
                    manufacturer=food_info['maker']
                )

                session.add(food)
                session.commit()
                saved_count += 1

                # 진행상황 출력
                if saved_count % 10 == 0:
                    print(f"   저장 중... {saved_count}/{len(filtered_items)}")

            except Exception as e:
                session.rollback()
                print(f"   ⚠️  오류 발생: {e}")
                continue

        # 7. 결과 확인
        print(f"\n[7/7] 결과 확인")
        print("=" * 60)
        print(f"✅ 완료!")
        print(f"   - 총 수집: {len(all_items)} 개")
        print(f"   - productType 필터링: {len(filtered_items)} 개")
        print(f"   - 저장 완료: {saved_count} 개")
        print(f"   - 중복 건너뜀: {skipped_count} 개")
        print(f"   - 신규 브랜드 발견: {len(new_brands)} 개")

        # 저장된 데이터 샘플 출력
        foods = session.query(Food).limit(5).all()
        print(f"\n📦 저장된 사료 샘플 (최대 5개):")
        for i, food in enumerate(foods, 1):
            brand_name = food.brand.name if food.brand else "알 수 없음"
            print(f"   [{i}] {food.name}")
            print(f"       브랜드: {brand_name}")
            print(f"       카테고리: {food.category}")
            print(f"       가격: {food.min_price:,} 원 ~ {food.max_price:,} 원" if food.min_price else "       가격: 정보 없음")

        print(f"\n📊 DB 통계:")
        print(f"   - 총 브랜드: {session.query(Brand).count()} 개")
        print(f"   - 총 사료: {session.query(Food).count()} 개")

        # DB 파일 정보 출력
        print(f"\n💾 DB 파일: cat_data.db")
        print(f"   파일 크기: {os.path.getsize('cat_data.db') / 1024:.2f} KB")

    finally:
        db.disconnect()
        print("\n" + "=" * 60)
        print("✅ 전체 프로세스 완료!")
        print("=" * 60)


if __name__ == '__main__':
    import sys

    # 커맨드 라인 인자 처리
    max_results = 100
    reset_db = True

    if len(sys.argv) > 1:
        try:
            max_results = int(sys.argv[1])
        except ValueError:
            print("⚠️  첫 번째 인자는 정수여야 합니다. 기본값 100을 사용합니다.")

    if len(sys.argv) > 2:
        reset_db = sys.argv[2].lower() in ['true', '1', 'yes']

    run_all(max_results=max_results, reset_db=reset_db)
