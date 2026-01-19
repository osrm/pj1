"""
인기 사료 수집 스크립트
네이버 쇼핑 API를 사용하여 상위 인기 사료 데이터를 수집합니다.
"""
from database.connection import db
from fetchers.naver_api import NaverShoppingAPI
from processors.formula_matcher import FormulaMatcher
from models.brand import Brand
from models.food import Food
from sqlalchemy.orm import Session
import click
from tqdm import tqdm


def save_brand(session: Session, brand_name: str) -> Brand:
    """
    브랜드 저장 (중복 시 기존 브랜드 반환)

    Args:
        session: DB 세션
        brand_name: 브랜드명

    Returns:
        브랜드 모델 인스턴스
    """
    brand = session.query(Brand).filter_by(name=brand_name).first()

    if not brand:
        brand = Brand(name=brand_name)
        session.add(brand)
        session.commit()
        session.refresh(brand)

    return brand


def fetch_and_save_foods(
    max_results: int = 100,
    query: str = "고양이 사료",
    reset: bool = False
):
    """
    네이버 API에서 사료 데이터 수집 및 저장

    Args:
        max_results: 최대 수집 개수
        query: 검색어
        reset: 기존 데이터 삭제 여부
    """
    db.connect()

    if reset:
        click.echo("기존 사료 데이터 삭제 중...")
        db.get_session().query(Food).delete()
        db.get_session().commit()

    try:
        # 네이버 API 클라이언트 초기화
        api = NaverShoppingAPI()
        matcher = FormulaMatcher()

        # 데이터 수집
        click.echo(f"네이버 쇼핑 검색 중... (query: {query}, max: {max_results})")
        items = api.fetch_all_cat_foods(
            max_results=max_results,
            query=query
        )

        if not items:
            click.echo("검색 결과가 없습니다.")
            return

        # 데이터베이스에 저장
        session = db.get_session()
        saved_count = 0
        skipped_count = 0

        with tqdm(total=len(items), desc="데이터 저장 중") as pbar:
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
                        pbar.update(1)
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
                    pbar.update(1)

                except Exception as e:
                    session.rollback()
                    pbar.write(f"오류 발생: {e}")
                    continue

        click.echo(f"\n수집 완료! 저장: {saved_count}, 중복 건너뜀: {skipped_count}")

    except Exception as e:
        click.echo(f"오류 발생: {e}", err=True)
        raise

    finally:
        db.disconnect()


@click.command()
@click.option('--max', default=100, help='최대 수집 개수 (기본: 100)')
@click.option('--query', default='고양이 사료', help='검색어 (기본: "고양이 사료")')
@click.option('--reset', is_flag=True, help='기존 데이터 삭제 후 재수집')
def fetch_popular(max, query, reset):
    """
    네이버 쇼핑 API로 인기 사료 수집

    Usage:
        python scripts/fetch_popular.py                          # 기본 옵션 (100개)
        python scripts/fetch_popular.py --max 500              # 500개 수집
        python scripts/fetch_popular.py --query "프리미엄 고양이 사료"  # 커스텀 검색어
        python scripts/fetch_popular.py --reset                # 기존 데이터 삭제 후 재수집
    """
    fetch_and_save_foods(max_results=max, query=query, reset=reset)


if __name__ == '__main__':
    fetch_popular()
