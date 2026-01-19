# GitHub Actions 설정 가이드

## 1. GitHub Repository 생성

1. [GitHub](https://github.com/new) 접속
2. 새로운 Repository 생성
   - Repository name: `cat-data-lab`
   - Public 또는 Private (선택)
3. 코드 업로드:
   ```bash
   cd C:\Users\심성민\Desktop\새 폴더 (3)\cat-data-lab
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin <repository-url>
   git push -u origin main
   ```

---

## 2. GitHub Secrets 설정 (API 키)

### 네이버 API 키 등록

1. GitHub Repository → **Settings**
2. **Secrets and variables** → **Actions**
3. **New repository secret** 클릭
4. 다음 두 개의 Secret 등록:

   | Secret 이름 | 값 |
   |------------|---|
   | `NAVER_CLIENT_ID` | 네이버 Client ID |
   | `NAVER_CLIENT_SECRET` | 네이버 Client Secret |

5. **Add secret** 클릭

---

## 3. Workflow 실행

### 수동 실행

1. GitHub Repository → **Actions**
2. **Cat-Data Lab Data Collection** 클릭
3. **Run workflow** 클릭
4. **max_results** 선택 (50/100/200/500)
5. **Run workflow** 클릭

### 자동 실행 (스케줄)

- **매일 자정 한국시간** (UTC 15:00)으로 설정됨
- `.github/workflows/data-collection.yml` 수정으로 변경 가능

### API 테스트

1. **Actions** → **Cat-Data Lab API Test**
2. **Run workflow** 클릭
3. 네이버 API 테스트 실행

---

## 4. 결과 확인

### 1. Workflow 로그 확인

1. **Actions** → 최신 workflow 클릭
2. 각 단계별 로그 확인
3. **Step 7: Show data summary**에서 DB 요약 확인

### 2. DB 파일 다운로드 (Artifact)

1. Workflow 완료 후
2. **Artifacts** 섹션
3. `cat-data-db-<run-number>` 다운로드
4. `cat_data.db` 파일 추출

### 3. 로컬에서 DB 확인

다운로드한 `cat_data.db`를 SQLite로 확인:

```bash
# Windows (SQLite3 설치 필요)
sqlite3 cat_data.db "SELECT COUNT(*) FROM foods;"
sqlite3 cat_data.db "SELECT f.name, b.name FROM foods f LEFT JOIN brands b ON f.brand_id = b.id LIMIT 10;"
```

---

## 5. Workflow 설정 수정

### 스케줄 변경

`.github/workflows/data-collection.yml` 수정:

```yaml
on:
  schedule:
    # 매주 월요일 오전 9시 한국시간 (UTC 0:00)
    - cron: '0 0 * * 1'
    # 매시 실행 (테스트용)
    - cron: '0 * * * *'
```

### 수집 개수 변경

**수동 실행시**: workflow_dispatch의 옵션 선택
**스케줄 실행시**: `.github/workflows/data-collection.yml` 수정:

```yaml
- name: Run data collection
  run: |
    python scripts/run_all_sqlite.py 500  # 기본 500개
```

---

## 6. GCS 연동 (선택)

### Google Cloud Storage에 DB 자동 업로드

1. **GCS Bucket 생성**
   - Google Cloud Console → Cloud Storage
   - 새 버킷 생성: `cat-data-lab-db`

2. **Service Account JSON 생성**
   - IAM → Service Accounts
   - 새 Service Account 생성
   - JSON 키 파일 다운로드

3. **GitHub Secret 등록**
   - Secret 이름: `GCS_CREDENTIALS`
   - 값: Service Account JSON 파일 내용

4. **Workflow 수정**
   ```yaml
   - name: Upload to GCS (optional)
     if: true  # false → true로 변경
     uses: 'google-github-actions/upload-cloud-storage@v2'
     with:
       path: 'cat_data.db'
       destination: 'cat-data-lab/db/'
       credentials_json: ${{ secrets.GCS_CREDENTIALS }}
   ```

---

## 7. 데이터 백업 전략

### GitHub Artifact (기본)
- 보관 기간: 30일
- 자동 삭제됨
- 테스트용으로 적합

### Google Cloud Storage (추천)
- 영구 보관
- 비용 발생 (사용량에 따라)
- 백업용으로 적합

### Local Backup (최후 수단)
- 로컬에 DB 파일 다운로드
- 수동 백업

---

## 8. 트러블슈팅

### Secret 설정 오류
```
Error: NAVER_CLIENT_ID is not set
```
- GitHub Secrets에 `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET` 등록 확인

### API 호출 실패
```
Error: 401 Unauthorized
```
- API 키 유효성 확인
- 네이버 개발자 센터에서 애플리케이션 상태 확인

### DB 파일 없음
```
cat_data.db: No such file or directory
```
- `scripts/run_all_sqlite.py`가 성공적으로 실행되었는지 확인
- Workflow 로그 확인

---

## 9. 확장 기능

### 여러 검색어로 수집

```yaml
- name: Run data collection (multiple queries)
  run: |
    python scripts/run_all_sqlite.py 100  # 고양이 사료
    python scripts/run_all_sqlite.py 50   # 프리미엄 고양이 사료
    python scripts/run_all_sqlite.py 50   # 저자극 고양이 사료
```

### 영양 성분 수집 추가

```yaml
- name: Fetch nutrition data
  run: |
    python scripts/fetch_nutrition.py --limit 100
```

### Slack/Email 알림

```yaml
- name: Send Slack notification
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
    payload: |
      {
        "text": "Cat-Data Lab 데이터 수집 완료! 🐱"
      }
```

---

## 10. 비용

| 리소스 | 비용 |
|--------|------|
| GitHub Actions (Public repo) | 무료 |
| GitHub Actions (Private repo) | 월 2,000분 무료 |
| Google Cloud Storage | $0.026/GB/월 |
| 네이버 API | 무료 (일일 25,000회) |

---

## 요약

1. **GitHub Repository 생성**
2. **GitHub Secrets**에 API 키 등록
3. **Workflow 수동 실행**으로 테스트
4. **스케줄 설정**으로 자동화
5. **Artifact 다운로드**로 DB 파일 확보
