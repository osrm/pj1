"""
데이터베이스 초기화 스크립트
"""
from database.connection import db
from database.migration import create_tables, drop_tables
import click


@click.command()
@click.option('--reset', is_flag=True, help='기존 테이블 삭제 후 재생성')
def init_db(reset):
    """
    데이터베이스 초기화

    Usage:
        python scripts/init_db.py              # 테이블 생성
        python scripts/init_db.py --reset       # 테이블 재생성
    """
    db.connect()

    try:
        if reset:
            click.echo("기존 테이블 삭제 중...")
            drop_tables()

        click.echo("테이블 생성 중...")
        create_tables()
        click.echo("데이터베이스 초기화 완료!")

    except Exception as e:
        click.echo(f"오류 발생: {e}", err=True)
        raise

    finally:
        db.disconnect()


if __name__ == '__main__':
    init_db()
