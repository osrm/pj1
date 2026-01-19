# AGENTS.md

Cat-Data Lab: 고양이 영양 데이터 분석 플랫폼 (Python 3.10+)

---

## Build, Test, and Run Commands

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Tests
```bash
# 네이버 API 연결 테스트
python scripts/test_naver_api.py

# 특정 테스트 실행 (pytest가 설정된 경우)
pytest tests/ -k test_name -v
```

### Run Application
```bash
# 전체 데이터 수집 실행 (3-Track 전략)
# 기본값: max_results=100, reset_db=True
python scripts/run_all_sqlite.py

# 결과 수 제한 지정
python scripts/run_all_sqlite.py 50

# DB 초기화하지 않고 실행
python scripts/run_all_sqlite.py 100 false

# 개별 스크립트 실행
python scripts/init_db.py           # DB 초기화
python scripts/fetch_popular.py     # 인기 사료 수집
python scripts/fetch_nutrition.py    # 영양 성분 수집
```

### Database Operations
```bash
# SQLite DB 직접 조회
sqlite3 cat_data.db

# 테이블 생성 (scripts 내에서 호출)
python -c "from database.migration_sqlite import create_tables; from database.connection_sqlite import db; db.connect(); create_tables()"
```

---

## Code Style Guidelines

### Imports
```python
# 1. 표준 라이브러리
import os
import re
from typing import Dict, List, Optional

# 2. 서드파티 라이브러리
import requests
from sqlalchemy import Column, Integer, String
from dotenv import load_dotenv

# 3. 로컬 임포트 (프로젝트 내부)
from config.settings import log_config
from models.food import Food
from utils.logger import setup_logger
```

### Type Hints
- 모든 함수에 타입 힌트 명시
- `Optional[T]`, `List[T]`, `Dict[K, V]`, `Tuple[...]` 활용
- 클래스 메서드는 `self` 타입 생략 가능

```python
def normalize_text(text: str) -> str:
    """기본 텍스트 정규화"""
    pass

def extract_brand(name: Optional[str]) -> Optional[str]:
    """브랜드명 추출"""
    pass

class NaverShoppingAPI:
    def search(self, query: str, display: int = 10) -> List[Dict]:
        """API 검색"""
        pass
```

### Naming Conventions
- **Functions/Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Private methods**: `_prefix`
- **Database tables**: `__tablename__ = 'snake_case_plural'`

```python
class DatabaseSQLite:  # PascalCase
    MAX_RETRIES = 3    # UPPER_CASE
    _connection = None # Private attribute

    def connect(self) -> bool:  # snake_case
        pass

    def _validate_config(self):  # Private method
        pass
```

### Docstrings
- 모든 모듈, 클래스, 함수에 한글/영문 docstring 작성
- Google Style 또는 Sphinx Style 사용
- Args, Returns 포함

```python
def search(
    self,
    query: str,
    display: int = 10,
    start: int = 1,
    sort: str = 'sim'
) -> List[Dict]:
    """
    네이버 쇼핑 검색 API 호출

    Args:
        query: 검색어
        display: 한 페이지에 보여질 결과 수 (최대 100)
        start: 검색 시작 위치 (최대 1000)
        sort: 정렬 옵션 (sim, date, asc, dsc)

    Returns:
        상품 리스트
    """
```

### Database Models (SQLAlchemy 2.0)
- 각 모델은 독립적인 `Base` 사용
- `__repr__` 메서드 포함
- 적절한 Column 타입과 제약 조건 사용
- Index는 필요한 필드에만 추가

```python
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Food(Base):
    """사료 테이블 모델"""
    __tablename__ = 'foods'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    brand_id = Column(Integer, ForeignKey('brands.id'), nullable=True)
    min_price = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Food(id={self.id}, name='{self.name}')>"
```

### Error Handling
- Try-except로 감싸되, 에러 메시지는 logging 사용
- DB 작업 시 세션 rollback 필수
- `ValueError`, `requests.exceptions.RequestException` 등 적절한 예외 타입 사용

```python
try:
    response = requests.get(url, headers=self.headers)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    logger.error(f"네이버 API 요청 실패: {e}")
    return []

# DB 작업에서의 에러 처리
try:
    session.add(food)
    session.commit()
except Exception as e:
    session.rollback()
    logger.error(f"데이터 저장 실패: {e}")
    raise
```

### Logging
- `utils/logger.py`의 `setup_logger()` 사용
- `logger.debug()`: 디버깅 정보
- `logger.info()`: 일반 진행 상황
- `logger.warning()`: 경고 (예외 처리 가능)
- `logger.error()`: 에러 (작업 실패)

```python
from utils.logger import setup_logger

logger = setup_logger(__name__)

logger.info(f"{total_fetched}/{max_results} 개 상품 수집 완료")
logger.warning("브랜드 정보를 찾을 수 없습니다")
logger.error(f"API 요청 실패: {e}")
```

### Configuration
- 환경 변수는 `.env` 파일 관리
- `config/database.py`에 config 클래스 정의
- `config/settings.py`에서 전역 인스턴스 생성

```python
# 환경 변수 사용
NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///cat_data.db')

# Config 클래스
class LogConfig:
    def __init__(self):
        self.level = os.getenv('LOG_LEVEL', 'INFO')
        self.format = os.getenv('LOG_FORMAT', '%(asctime)s - ...')

# 전역 인스턴스
log_config = LogConfig()
```

### String Processing
- HTML 태그 제거: `re.sub(r'<[^>]+>', '', text)`
- 공백 정규화: `re.sub(r'\s+', ' ', text).strip()`
- 유니코드 정규화: `unicodedata.normalize('NFC', text)`
- 브랜드명 매칭 시 대소문자 무시

---

## Project Structure

```
pj1/
├── config/              # 설정 (DB, API, 로그)
│   ├── database.py      # Config classes
│   └── settings.py      # Global instances
├── models/              # DB 모델 (Brand, Food, Nutrition, Ingredient)
├── fetchers/            # 데이터 수집
│   └── naver_api.py    # 네이버 쇼핑 API
├── processors/          # 데이터 처리
│   ├── formula_matcher.py      # 제품명 파싱
│   └── duplicate_remover.py    # 중복 제거
├── database/            # DB 유틸리티
│   ├── connection_sqlite.py    # SQLite 연결
│   └── migration_sqlite.py     # 테이블 생성/삭제
├── scripts/             # 실행 스크립트
│   ├── test_naver_api.py       # API 테스트
│   ├── run_all_sqlite.py       # 전체 실행
│   ├── init_db.py              # DB 초기화
│   ├── fetch_popular.py        # 인기 사료 수집
│   └── fetch_nutrition.py      # 영양 성분 수집
├── utils/               # 유틸리티
│   ├── logger.py        # 로깅 설정
│   ├── normalizer.py    # 텍스트 정규화
│   └── validators.py    # 데이터 검증
├── .github/workflows/   # GitHub Actions
│   ├── data-collection.yml      # 데이터 수집 워크플로우
│   └── api-test.yml             # API 테스트 워크플로우
├── .env                 # 환경 변수 (API 키 등)
├── requirements.txt      # Python 의존성
├── brands.json          # 브랜드 사전 (수집 대상)
└── cat_data.db          # SQLite DB (자동 생성)
```

---

## Important Notes

1. **3-Track 전략**: 브랜드 기반 검색(Track A) → 가격대 슬라이싱(Track B) → 신규 브랜드 발견(Track C)
2. **데이터 필터링**: `productType=2` (카탈로그 상품) 우선, 카테고리 포함 '사료' 체크
3. **중복 제거**: `naver_product_id` 기반 중복 제거 필수
4. **텍스트 정규화**: `TextNormalizer` 클래스 사용하여 브랜드명, 사료명, 가격 정규화
5. **세션 관리**: DB 세션 사용 후 반드시 `close()` 또는 context manager 사용
6. **GitHub Actions**: 매일 자정(UTC 15:00) 자동 실행, Artifact로 DB 파일 저장

---

## Environment Variables

Required in `.env`:
```env
NAVER_CLIENT_ID=your_client_id
NAVER_CLIENT_SECRET=your_client_secret
```

Optional:
```env
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///cat_data.db
MAX_RETRIES=3
REQUEST_DELAY=1
MAX_CONCURRENT_REQUESTS=10
```
