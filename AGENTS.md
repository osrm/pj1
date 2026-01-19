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
```

**참고**: 이 프로젝트는 pytest를 사용하지 않습니다. 테스트는 개별 스크립트로 실행합니다.

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

## Private Repo Database Storage

### Why Private Repo?
DB 파일(`cat_data.db`)을 public repo에 저장하면 데이터 노출 위험이 있습니다. `pj1_DB` private repo를 별도로 생성하여 DB를 저장합니다.

### Method 1: GitHub Actions Direct Clone/Push (RECOMMENDED)

#### Step 1: Create pj1_DB Private Repo
```bash
# 새로운 private repo 생성
# https://github.com/new
```

#### Step 2: Create GitHub Token for pj1_DB
1. GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
2. Generate new token → **repo** scope 선택 (필수)
3. Token 복사

#### Step 3: Add Token to pj1 Secrets
1. `pj1` repo → Settings → Secrets and variables → Actions
2. New secret: `PJ1_DB_TOKEN` = (생성한 토큰 값)
3. New secret: `PJ1_DB_REPO` = `osrm/pj1_DB` (당신의 repo 경로)

#### Step 4: Modify Workflow to Push to pj1_DB

```yaml
# .github/workflows/data-collection.yml에 추가 (Artifact 업로드 이전)
- name: Clone pj1_DB private repo
  run: |
    git clone https://${{ secrets.PJ1_DB_TOKEN }}@github.com/${{ secrets.PJ1_DB_REPO }}.git pj1_DB

- name: Copy DB to pj1_DB
  run: cp cat_data.db pj1_DB/

- name: Commit and push to pj1_DB
  working-directory: ./pj1_DB
  run: |
    git config user.email "action@github.com"
    git config user.name "GitHub Action"
    git add cat_data.db
    git diff --quiet && git diff --staged --quiet || git commit -m "Update DB from pj1 workflow"
    git push origin main
```

### Method 2: Git Submodule

```bash
# 현재 잘못 복사된 디렉토리 삭제
rm -rf pj1_DB

# submodule로 추가
git submodule add https://github.com/osrm/pj1_DB.git pj1_DB

# submodule 초기화
git submodule update --init --recursive
```

**주의**: Submodule 방식은 pj1_DB repo의 변경사항을 자동으로 pull하지 않습니다. 별도 관리가 필요합니다.

---

## Code Style Guidelines

### Imports
```python
# 1. 표준 라이브러리
import os
import re
import logging
from typing import Dict, List, Optional

# 2. 서드파티 라이브러리
import requests
from sqlalchemy import Column, Integer, String
from dotenv import load_dotenv

# 3. 로컬 임포트 (프로젝트 내부)
from config.settings import log_config
from models.food import Food
from fetchers.naver_api import NaverShoppingAPI
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
```python
# 방법 1: 표준 logging 모듈 사용 (현재 프로젝트 기본)
import logging

logging.basicConfig(level=log_config.level, format=log_config.format)
logger = logging.getLogger(__name__)

# 방법 2: utils/logger.py 사용 (선택 사항)
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
- HTML 태그 제거: `re.sub(r'<[^>]+>', '', text)` 또는 `text.replace('<b>', '').replace('</b>', '')`
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
6. **GitHub Actions**: 매일 자정(UTC 15:00) 자동 실행, Artifact로 DB 파일 저장 + private repo push

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

GitHub Secrets for private repo DB storage:
```env
PJ1_DB_TOKEN=your_github_token_with_repo_scope
PJ1_DB_REPO=username/pj1_DB
```

---

## GitHub Actions Workflow Pattern

```yaml
name: Cat-Data Lab Data Collection

on:
  schedule:
    - cron: '0 15 * * *'  # 매일 자정 한국시간
  workflow_dispatch:
    inputs:
      max_results:
        description: '브랜드당/가격대별 최대 결과 수'
        required: false
        default: '100'

jobs:
  collect-data:
    runs-on: ubuntu-latest
    steps:
      # 체크아웃
      - uses: actions/checkout@v4

      # Python 설정
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'

      # 의존성 설치
      - run: pip install -r requirements.txt

      # API 테스트
      - run: PYTHONPATH=. python scripts/test_naver_api.py
        env:
          NAVER_CLIENT_ID: ${{ secrets.NAVER_CLIENT_ID }}
          NAVER_CLIENT_SECRET: ${{ secrets.NAVER_CLIENT_SECRET }}

      # 데이터 수집
      - run: PYTHONPATH=. python scripts/run_all_sqlite.py ${{ github.event.inputs.max_results || '100' }}
        env:
          NAVER_CLIENT_ID: ${{ secrets.NAVER_CLIENT_ID }}
          NAVER_CLIENT_SECRET: ${{ secrets.NAVER_CLIENT_SECRET }}

      # pj1_DB private repo에 DB 저장
      - name: Clone pj1_DB private repo
        run: git clone https://${{ secrets.PJ1_DB_TOKEN }}@github.com/${{ secrets.PJ1_DB_REPO }}.git pj1_DB

      - name: Copy DB to pj1_DB
        run: cp cat_data.db pj1_DB/

      - name: Commit and push to pj1_DB
        working-directory: ./pj1_DB
        run: |
          git config user.email "action@github.com"
          git config user.name "GitHub Action"
          git add cat_data.db
          git diff --quiet && git diff --staged --quiet || git commit -m "Update DB from pj1 workflow"
          git push origin main

      # brands.json 업데이트 커밋
      - name: Commit brands.json updates
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git diff --quiet brands.json || git add brands.json && git commit -m "Update brands.json [skip ci]" || echo "No changes"

      # Artifact 업로드 (백업용)
      - uses: actions/upload-artifact@v4
        with:
          name: cat-data-db-${{ github.run_number }}
          path: cat_data.db
          retention-days: 30
```
