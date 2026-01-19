# Cat-Data Lab - Google Cloud에서 실행하기

## Google Cloud Shell에서 실행 방법

### 1. Google Cloud Shell 열기
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 상단의 "Cloud Shell" 아이콘 클릭 (>_)
3. 터미널이 열릴 때까지 기다림

### 2. 프로젝트 파일 업로드
```bash
# Google Cloud Shell에서
git clone <프로젝트 URL>  # GitHub에 업로드한 경우
# 또는 파일 직접 업로드 (Cloud Shell Editor 사용)
```

### 3. .env 파일에 네이버 API 키 입력
```bash
# .env 파일 수정
nano .env

# NAVER_CLIENT_ID=your_client_id_here
# NAVER_CLIENT_SECRET=your_client_secret_here
# 위 부분에 발급받은 키 입력 후 Ctrl+X, Y, Enter로 저장
```

### 4. 의존성 설치
```bash
pip install -r requirements.txt
```

### 5. 네이버 API 테스트
```bash
python scripts/test_naver_api.py
```

### 6. 전체 실행 (DB 초기화 + 데이터 수집)
```bash
python scripts/run_all.py
```

### 7. 결과 확인
```bash
# DB 파일 확인
ls -lh cat_data.db

# DB 내용 확인 (SQLite)
sqlite3 cat_data.db "SELECT COUNT(*) FROM foods;"
sqlite3 cat_data.db "SELECT name, brand_id FROM foods LIMIT 5;"
```

---

## 옵션

### 수집 개수 지정
```bash
python scripts/run_all.py 50      # 50개만 수집
python scripts/run_all.py 500     # 500개 수집
```

### DB 초기화 없이 추가 수집
```bash
# scripts/run_all.py 수정: reset_db=False
python scripts/run_all.py 100 False
```

---

## 파일 구조
```
cat-data-lab/
├── config/              - 설정
├── models/              - DB 모델
├── fetchers/            - 네이버 API
├── processors/          - Formula 매칭
├── database/            - DB 연결 (SQLite)
├── scripts/             - 실행 스크립트
│   ├── test_naver_api.py   - 네이버 API 테스트
│   └── run_all.py           - 전체 실행
├── .env                 - 환경 변수 (API 키)
└── requirements.txt     - 의존성
```

---

## 참고
- **데이터베이스**: SQLite (설치 불필요, 파일로 생성)
- **API**: 네이버 쇼핑 검색 API
- **Google Cloud Shell**: 무료 사용 (매일 5시간, 한달 60시간)
