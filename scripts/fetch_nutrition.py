"""
영양 성분 수집 스크립트
영양 성분 정보를 수집합니다.
"""
from database.connection import db
from models.food import Food
from models.nutrition import Nutrition
from models.ingredient import Ingredient
from sqlalchemy.orm import Session
import click
from tqdm import tqdm


def fetch_nutrition(food_id: int) -> dict:
    """
    특정 사료의 영양 성분 수집

    Args:
        food_id: 사료 ID

    Returns:
        영양 성분 딕셔너리
    """
    session = db.get_session()
    food = session.query(Food).get(food_id)

    if not food:
        return {}

    # TODO: 브랜드별 크롤러 구현
    # 현재는 더미 데이터 반환

    nutrition_data = {
        'protein': 38.0,
        'fat': 20.0,
        'fiber': 3.0,
        'moisture': 10.0,
        'ash': 8.0,
        'carbs': 21.0  # 100 - (protein + fat + fiber + moisture + ash)
    }

    return nutrition_data


def save_nutrition(session: Session, food_id: int, nutrition_data: dict):
    """
    영양 성분 저장

    Args:
        session: DB 세션
        food_id: 사료 ID
        nutrition_data: 영양 성분 데이터
    """
    # 기존 영양 성분이 있으면 업데이트
    existing = session.query(Nutrition).filter_by(food_id=food_id).first()

    if existing:
        for key, value in nutrition_data.items():
            setattr(existing, key, value)
    else:
        nutrition = Nutrition(food_id=food_id, **nutrition_data)
        session.add(nutrition)

    session.commit()


@click.command()
@click.option('--limit', default=10, help='수집할 사료 개수 (기본: 10)')
@click.option('--offset', default=0, help='시작 오프셋 (기본: 0)')
def fetch_nutritions(limit, offset):
    """
    영양 성분 수집

    Usage:
        python scripts/fetch_nutrition.py                    # 기본 옵션 (10개)
        python scripts/fetch_nutrition.py --limit 50          # 50개 수집
        python scripts/fetch_nutrition.py --offset 10        # 10번째부터 수집
    """
    db.connect()

    try:
        session = db.get_session()

        # 수집 대상 사료 조회
        foods = session.query(Food).offset(offset).limit(limit).all()

        if not foods:
            click.echo("수집 대상 사료가 없습니다.")
            return

        click.echo(f"{len(foods)}개 사료의 영양 성분 수집 중...")

        with tqdm(total=len(foods), desc="영양 성분 수집") as pbar:
            for food in foods:
                try:
                    # 영양 성분 수집
                    nutrition_data = fetch_nutrition(food.id)

                    # 저장
                    save_nutrition(session, food.id, nutrition_data)

                    pbar.update(1)

                except Exception as e:
                    session.rollback()
                    pbar.write(f"오류 발생 (ID: {food.id}): {e}")
                    continue

        click.echo(f"\n영양 성분 수집 완료!")

    except Exception as e:
        click.echo(f"오류 발생: {e}", err=True)
        raise

    finally:
        db.disconnect()


if __name__ == '__main__':
    fetch_nutritions()
