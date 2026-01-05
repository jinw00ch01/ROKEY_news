# 배포 가이드 (Render.com)

이 문서는 Render.com을 사용하여 PostgreSQL DB, 백엔드(FastAPI), 프론트엔드(React)를 배포하고 GitHub Actions CI를 연동하는 절차를 안내합니다.

## 준비물
- GitHub 저장소 (`main` 브랜치)
- Google Gemini API 키 ([발급](https://ai.google.dev/))
- finnhub API 키 ([발급](https://finnhub.io/))
- NEWSDATA.io API 키 ([발급](https://newsdata.io/))
- Render 계정

## 전체 구조

```
GitHub Repository
    ↓
Render.com
├── PostgreSQL (Database)
├── Web Service (Backend - FastAPI)
└── Static Site (Frontend - React)
```

## 1. Render PostgreSQL 데이터베이스 생성

1. [Render Dashboard](https://dashboard.render.com/) → **New** → **PostgreSQL**
2. 데이터베이스 이름 입력 (예: `rokey-news-db`)
3. **Create Database** 클릭
4. 생성 완료 후 **Connections** 탭에서 **Internal Database URL** 복사
   - 형식: `postgresql://user:password@host:5432/dbname`
   - 이 URL을 백엔드 환경 변수로 사용

## 2. 백엔드 (Web Service) 배포

### 2-1. Web Service 생성

1. Render Dashboard → **New** → **Web Service**
2. GitHub 저장소 연결
3. 설정:
   - **Name**: `rokey-news-backend`
   - **Branch**: `main`
   - **Runtime**: **Python 3.11+**
   - **Root Directory**: `backend`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port 10000
     ```

### 2-2. 백엔드 환경 변수 설정

Render Web Service 설정 페이지 → **Environment** 탭에서 다음 환경 변수 추가:

| 키 | 값 | 설명 |
|---|---|---|
| `GEMINI_API_KEY` | `your_gemini_key` | Google Gemini API 키 |
| `FINNHUB_API_KEY` | `your_finnhub_key` | finnhub API 키 |
| `NEWSDATA_API_KEY` | `your_newsdata_key` | NEWSDATA.io API 키 |
| `DATABASE_URL` | `postgresql://...` | Render PostgreSQL Internal URL |
| `ALLOWED_ORIGINS` | `https://your-frontend.onrender.com` | 프론트엔드 도메인 (CORS) |
| `RATE_LIMIT_PER_MIN` | `60` | API 레이트 리밋 |

**중요**: 환경 변수 추가 후 **Save Changes** → 자동 재배포

### 2-3. 백엔드 URL 확인

- 배포 완료 후 URL 확인 (예: `https://rokey-news-backend.onrender.com`)
- 헬스체크 확인: `https://your-backend.onrender.com/health`
- API 문서 확인: `https://your-backend.onrender.com/docs`

## 3. 프론트엔드 (Static Site) 배포

### 3-1. Static Site 생성

1. Render Dashboard → **New** → **Static Site**
2. GitHub 저장소 연결
3. 설정:
   - **Name**: `rokey-news-frontend`
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**:
     ```bash
     npm install && npm run build
     ```
   - **Publish Directory**: `dist`

### 3-2. 프론트엔드 환경 변수 설정

Render Static Site 설정 페이지 → **Environment** 탭에서 환경 변수 추가:

| 키 | 값 | 설명 |
|---|---|---|
| `VITE_API_BASE_URL` | `https://your-backend.onrender.com` | 백엔드 API URL |

**중요**: 환경 변수 추가 후 **Save** → 재배포 트리거

### 3-3. 프론트엔드 URL 확인

- 배포 완료 후 URL 확인 (예: `https://rokey-news-frontend.onrender.com`)
- 백엔드의 `ALLOWED_ORIGINS`에 이 URL이 포함되어 있는지 확인

## 4. 백엔드 CORS 설정 업데이트

프론트엔드 URL을 백엔드의 `ALLOWED_ORIGINS`에 추가:

1. 백엔드 Web Service → **Environment** 탭
2. `ALLOWED_ORIGINS` 값을 프론트엔드 URL로 업데이트
   ```
   https://rokey-news-frontend.onrender.com
   ```
3. **Save Changes** → 자동 재배포

## 5. 데이터베이스 마이그레이션

백엔드가 처음 배포되면 데이터베이스 테이블을 생성해야 합니다.

### 옵션 1: 로컬에서 마이그레이션 실행

```bash
cd backend
# Render DATABASE_URL 사용
export DATABASE_URL="postgresql://..."
alembic upgrade head
```

### 옵션 2: Render Shell에서 실행

1. 백엔드 Web Service → **Shell** 탭
2. 다음 명령 실행:
   ```bash
   cd /opt/render/project/src/backend
   alembic upgrade head
   ```

## 6. GitHub Actions 자동 배포 설정 (선택)

### 6-1. Render API Key 발급

1. [Render Account Settings](https://dashboard.render.com/account) → **API Keys**
2. **Create API Key** → 키 복사

### 6-2. GitHub Secrets 설정

GitHub 저장소 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

추가할 시크릿:

| 이름 | 값 | 설명 |
|---|---|---|
| `RENDER_API_KEY` | `rnd_...` | Render API Key |
| `RENDER_SERVICE_ID` | 백엔드 Service ID | 백엔드 Web Service ID |
| `RENDER_STATIC_ID` | 프론트엔드 Site ID | 프론트엔드 Static Site ID |

**Service ID 찾기**:
- 백엔드: Web Service URL에서 확인 (예: `srv-xxxxx`)
- 프론트엔드: Static Site URL에서 확인 (예: `stc-xxxxx`)

### 6-3. GitHub Actions 워크플로 확인

`.github/workflows/` 디렉터리에 다음 워크플로가 있는지 확인:
- `ci-backend.yml`: 백엔드 테스트
- `ci-frontend.yml`: 프론트엔드 lint & build
- `deploy-backend.yml`: 백엔드 자동 배포 (선택)
- `deploy-frontend.yml`: 프론트엔드 자동 배포 (선택)

## 7. 배포 후 점검

### 7-1. 백엔드 헬스체크
```bash
curl https://your-backend.onrender.com/health
# 응답: {"status": "ok"}
```

### 7-2. 뉴스 수집 테스트
```bash
curl -X POST https://your-backend.onrender.com/admin/ingest/run
# 응답: {"fetched": N, "analyzed": M}
```

### 7-3. 프론트엔드 접속
- 브라우저에서 프론트엔드 URL 접속
- 기사 목록이 표시되는지 확인
- 개발자 도구 → **Network** 탭에서 API 호출 확인

### 7-4. CORS 확인
- 프론트엔드에서 API 호출 시 CORS 에러가 없는지 확인
- 에러 발생 시 백엔드의 `ALLOWED_ORIGINS` 재확인

## 8. 자주 묻는 문제 (FAQ)

### Q1: CORS 에러가 발생합니다
**A**: 백엔드의 `ALLOWED_ORIGINS`에 프론트엔드 URL이 정확히 포함되어 있는지 확인하세요.
```
ALLOWED_ORIGINS=https://your-frontend.onrender.com
```

### Q2: DATABASE_URL 에러가 발생합니다
**A**: Render PostgreSQL의 **Internal Database URL**을 사용하세요. External URL이 아닙니다.

### Q3: API 키 에러가 발생합니다
**A**: 다음을 확인하세요:
- `GEMINI_API_KEY`가 올바른지
- `FINNHUB_API_KEY`가 올바른지
- `NEWSDATA_API_KEY`가 올바른지
- 각 API의 무료 플랜 제한을 초과하지 않았는지

### Q4: 데이터베이스 마이그레이션이 필요합니다
**A**: 
```bash
# 로컬에서 실행
export DATABASE_URL="postgresql://..."
cd backend
alembic upgrade head
```

### Q5: 백엔드가 시작되지 않습니다
**A**: Render 로그를 확인하세요:
- Web Service → **Logs** 탭
- 환경 변수 오타, 의존성 설치 실패 등을 확인

### Q6: API 호출 제한을 초과했습니다
**A**: 
- finnhub: 무료 플랜은 60 calls/minute
- NEWSDATA.io: 무료 플랜은 200 credits/day
- 유료 플랜으로 업그레이드하거나 호출 빈도 조정

## 9. 환경 변수 요약

### 백엔드 (Web Service)
```env
GEMINI_API_KEY=your_gemini_key
FINNHUB_API_KEY=your_finnhub_key
NEWSDATA_API_KEY=your_newsdata_key
DATABASE_URL=postgresql://user:password@host:5432/dbname
ALLOWED_ORIGINS=https://your-frontend.onrender.com
RATE_LIMIT_PER_MIN=60
```

### 프론트엔드 (Static Site)
```env
VITE_API_BASE_URL=https://your-backend.onrender.com
```

## 10. 추가 리소스

- [Render 문서](https://render.com/docs)
- [FastAPI 배포 가이드](https://fastapi.tiangolo.com/deployment/)
- [Vite 배포 가이드](https://vitejs.dev/guide/static-deploy.html)
- [Alembic 문서](https://alembic.sqlalchemy.org/)
