# Cat-Data Lab

고양이 영양 데이터 분석 플랫폼

[![Data Collection](https://github.com/your-username/cat-data-lab/actions/workflows/data-collection.yml/badge.svg)](https://github.com/your-username/cat-data-lab/actions/workflows/data-collection.yml)
[![API Test](https://github.com/your-username/cat-data-lab/actions/workflows/api-test.yml/badge.svg)](https://github.com/your-username/cat-data-lab/actions/workflows/api-test.yml)

## 🚀 GitHub Actions로 데이터 수집

### ⚡ 빠른 시작

1. **GitHub Repository 생성 및 코드 업로드**
2. **GitHub Secrets**에 네이버 API 키 등록
   - `NAVER_CLIENT_ID`
   - `NAVER_CLIENT_SECRET`
3. **Actions** → **Run workflow** 클릭
4. 완료 후 **Artifact**에서 `cat_data.db` 다운로드

### 📖 자세한 가이드

- [GitHub Actions 설정 가이드](GITHUB_ACTIONS.md)
- [Google Cloud 실행 가이드](GOOGLE_CLOUD.md)
- [빠른 시작 가이드](QUICKSTART.md)

---

## 📁 프로젝트 구조

```
cat-data-lab/
├── config/                    - 설정 (DB, API, 로그)
├── models/                    - DB 모델 (Brand, Food, Nutrition, Ingredient)
├── fetchers/                  - 데이터 수집
│   └── naver_api.py           - 네이버 쇼핑 검색 API
├── processors/                - 데이터 처리
│   └── formula_matcher.py     - Formula 방식 매칭
├── database/                  - DB 유틸리티
│   ├── connection_sqlite.py   # SQLite 연결
│   └── migration_sqlite.py    # 테이블 생성/삭제
├── scripts/                   - 실행 스크립트
│   ├── test_naver_api.py      # 네이버 API 테스트
│   └── run_all_sqlite.py      # 전체 실행
├── .github/workflows/         - GitHub Actions 워크플로우
│   ├── data-collection.yml    # 데이터 수집
│   └── api-test.yml           # API 테스트
├── .env                       - 환경 변수 (API 키)
├── requirements.txt           - 의존성
├── QUICKSTART.md              - 빠른 시작 가이드
├── GITHUB_ACTIONS.md           - GitHub Actions 가이드
└── GOOGLE_CLOUD.md            - Google Cloud 가이드
```

---

## 📊 DB 스키마

### Brand (브랜드)
- id, name, country, official_url

### Food (사료)
- id, name, brand_id, category, type, size, min_price, max_price, link, image, naver_product_id, manufacturer

### Nutrition (영양 성분)
- id, food_id, protein, fat, fiber, moisture, ash, carbs, calories, calcium, phosphorus, taurine, omega_3, omega_6

### Ingredient (성분)
- id, food_id, rank, name, is_grain, is_byproduct, is_meat, is_synthetic, is_preservative, is_coloring, is_flavor, percentage, description

---

## 🔄 Workflow

### Data Collection Workflow
- **트리거**: 매일 자정 (UTC 15:00) 또는 수동 실행
- **수집 개수**: 50/100/200/500 (선택 가능)
- **결과**: `cat_data.db` 파일을 Artifact로 저장

### API Test Workflow
- **트리거**: 수동 실행
- **기능**: 네이버 API 테스트

---

## 🛠️ 로컬에서 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. .env 파일 설정
```env
NAVER_CLIENT_ID=your_client_id
NAVER_CLIENT_SECRET=your_client_secret
```

### 3. 네이버 API 테스트
```bash
python scripts/test_naver_api.py
```

### 4. 전체 실행
```bash
python scripts/run_all_sqlite.py
```

---

## 📝 데이터 수집 방식

1. **네이버 쇼핑 API** → 상위 인기 사료 리스트 수집
2. **Formula 방식 매칭** → 브랜드, 연령, 카테고리, 사이즈 추출
3. **DB 저장** → SQLite 파일로 저장
4. **Artifact 업로드** → GitHub Actions 결과 저장

---

## 🎯 다음 단계

- [ ] 영양 성분 자동 파싱
- [ ] 성분 정보 자동 태깅
- [ ] GCS 연동으로 영구 백업
- [ ] 데이터 분석 및 시각화

---

## 📄 라이선스

MIT License

---

## 🤝 기여

Pull Request를 환영합니다!

---

**작성자:** Cat-Data Lab 팀
**버전:** 1.0
**작성일:** 2026년 1월 19일
