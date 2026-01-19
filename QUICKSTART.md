# Cat-Data Lab - 빠른 시작

## 네이버 API 키 설정

1. `.env` 파일 열기
2. 네이버 API 키 입력:
```env
NAVER_CLIENT_ID=발급받은_Client_ID
NAVER_CLIENT_SECRET=발급받은_Client_Secret
```

## 실행 방법 (Google Cloud)

### 1. Google Cloud Shell 열기
- [Google Cloud Console](https://console.cloud.google.com/)
- 상단 "Cloud Shell" 아이콘 클릭

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 네이버 API 테스트
```bash
python scripts/test_naver_api.py
```

### 4. 전체 실행 (데이터 수집)
```bash
python scripts/run_all_sqlite.py
```

### 5. 옵션
```bash
python scripts/run_all_sqlite.py 50       # 50개만 수집
python scripts/run_all_sqlite.py 500      # 500개 수집
```

## 결과 확인

### DB 파일 확인
```bash
ls -lh cat_data.db
```

### DB 내용 확인 (SQLite)
```bash
sqlite3 cat_data.db "SELECT COUNT(*) FROM foods;"
sqlite3 cat_data.db "SELECT name, brand_id FROM foods LIMIT 5;"
```

### Python으로 확인
```bash
python -c "
from database.connection_sqlite import db
from models.food import Food
db.connect()
session = db.get_session()
foods = session.query(Food).all()
for f in foods:
    brand = f.brand.name if f.brand else '알 수 없음'
    print(f'{brand}: {f.name}')
db.disconnect()
"
```

## 파일 구조
```
cat-data-lab/
├── config/                 - 설정
├── models/                 - DB 모델 (Brand, Food, Nutrition, Ingredient)
├── fetchers/               - 네이버 API
│   └── naver_api.py        - 네이버 쇼핑 검색 API
├── processors/             - Formula 매칭
│   └── formula_matcher.py  - 제품명 파싱
├── database/               - DB 연결 (SQLite)
│   ├── connection_sqlite.py  # SQLite 연결
│   └── migration_sqlite.py   # 테이블 생성/삭제
├── scripts/                - 실행 스크립트
│   ├── test_naver_api.py      # 네이버 API 테스트
│   └── run_all_sqlite.py      # 전체 실행
├── .env                    - 환경 변수 (API 키)
└── requirements.txt        - 의존성
```

## DB 스키마

### Brand (브랜드)
- id: 브랜드 ID
- name: 브랜드명
- country: 국가
- official_url: 공식 URL

### Food (사료)
- id: 사료 ID
- name: 사료명
- brand_id: 브랜드 ID
- category: 카테고리 (dry, wet, freeze_dried)
- type: 연령 (kitten, adult, senior)
- size: 사이즈 (예: 5.4kg)
- min_price: 최저가
- max_price: 최고가
- link: 상품 링크
- image: 상품 이미지 URL
- naver_product_id: 네이버 상품 ID

### Nutrition (영양 성분)
- id: 영양 성분 ID
- food_id: 사료 ID
- protein: 단백질 %
- fat: 지방 %
- fiber: 섬유소 %
- moisture: 수분 %
- ash: 회분 %
- carbs: 탄수화물 %

### Ingredient (성분)
- id: 성분 ID
- food_id: 사료 ID
- rank: 원료 순서
- name: 원료명
- is_grain: 곡물 여부
- is_byproduct: 부산물 여부
- is_meat: 고기/생선 여부
- is_synthetic: 합성 첨가물 여부

## 다음 단계

1. 네이버 API 테스트: `python scripts/test_naver_api.py`
2. 전체 실행: `python scripts/run_all_sqlite.py`
3. 결과 확인: DB 파일 및 내용 확인
4. 데이터 분석: 저장된 데이터를 활용하여 분석 진행

## 참고

- **데이터베이스**: SQLite (설치 불필요, 파일로 생성)
- **API**: 네이버 쇼핑 검색 API
- **수집 방식**: 네이버 API → Formula 매칭 → DB 저장
- **추가 확장**: 브랜드 홈페이지 크롤러 → 영양 성분 수집
