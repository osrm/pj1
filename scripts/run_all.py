"""
전체 실행 스크립트
DB 초기화 → 네이버 API로 데이터 수집 → 결과 확인까지 한번에 실행
"""
from database.connection import db
from database.migration import create_tables, drop_tables
from fetchers.naver_api import NaverShoppingAPI
from processors.formula_matcher import FormulaMatcher
from models.brand import Brand
from models.food import Food
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
    전체 프로세스 실행

    Args:
        max_results: 수집할 최대 사료 개수
        reset_db: DB 초기화 여부
    """
    print("=" * 60)
    print("Cat-Data Lab 전체 실행")
    print("=" * 60)

    # 1. DB 연결
    print("\n[1/5] 데이터베이스 연결 중...")
    db.connect()

    try:
        # 2. 테이블 생성
        print(f"[2/5] 테이블 생성 중... (초기화: {reset_db})")
        if reset_db:
            drop_tables()
        create_tables()

        # 3. 네이버 API로 데이터 수집
        print(f"\n[3/5] 네이버 쇼핑에서 인기 사료 수집 중... (최대 {max_results}개)")
        api = NaverShoppingAPI()
        matcher = FormulaMatcher()

        items = api.fetch_all_cat_foods(
            max_results=max_results,
            query="고양이 사료"
        )

        if not items:
            print("❌ 검색 결과가 없습니다.")
            return

        # 4. 데이터베이스에 저장
        print(f"\n[4/5] 데이터베이스에 저장 중...")
        session = db.get_session()
        saved_count = 0
        skipped_count = 0

        for item in items:
            try:
                # 사료 정보 추출
                food_info = api.extract_food_info(item)

                # Formula 방식 매칭
                parsed = matcher.parse_product_name(food_info['name'])

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
                    print(f"   저장 중... {saved_count}/{len(items)}")

            except Exception as e:
                session.rollback()
                print(f"   ⚠️  오류 발생: {e}")
                continue

        # 5. 결과 확인
        print(f"\n[5/5] 결과 확인")
        print("=" * 60)
        print(f"✅ 완료!")
        print(f"   - 총 수집: {len(items)} 개")
        print(f"   - 저장 완료: {saved_count} 개")
        print(f"   - 중복 건너뜀: {skipped_count} 개")

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
