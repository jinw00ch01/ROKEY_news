# Rokey News 요약/감성 분석 웹앱

RSS 기반 뉴스를 수집해 Gemini로 요약/감성 분석하고, 웹에서 검색·필터링·열람할 수 있는 서비스입니다. 프런트(Vite+React)와 백엔드(FastAPI)로 구성됩니다.

```mermaid
flowchart TD
  rss[RSS Feeds] --> fetcher[Fetcher]
  fetcher --> preprocess[Clean]
  preprocess --> analyzer[Gemini Analyzer]
  analyzer --> db[(DB)]
  db --> api[FastAPI API]
  api --> web[React Web]
```

## 기술 스택

### Backend
- **Framework**: FastAPI 0.115.0
- **Database**: SQLAlchemy 2.0.37 + PostgreSQL (psycopg 3.2.12)
- **Migration**: Alembic 1.14.0
- **AI**: Google Gemini API
- **RSS**: feedparser 6.0.11

### Frontend
- **Framework**: React 18 + TypeScript
- **Build**: Vite
- **Routing**: React Router
- **Data Fetching**: TanStack Query (React Query)
- **Styling**: Tailwind CSS

### DevOps
- **CI/CD**: GitHub Actions
- **Deployment**: Render.com (Web Service + Static Site + PostgreSQL)
- **Testing**: pytest (Backend), ESLint (Frontend)

## 디렉터리 구조
- `backend/` FastAPI 서비스
- `frontend/` Vite+React 웹
- `docs/` 기획·설계 문서
- `.github/workflows/` CI/CD 파이프라인

```mermaid
graph LR
  A[frontend] -->|REST| B[(backend API)]
  B --> C[(PostgreSQL)]
  B --> D[Gemini API]
```

## 빠른 시작

### 백엔드 (로컬)
```bash
cd backend
python -m venv .venv && .venv/Scripts/activate   # Windows
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- 헬스체크: http://localhost:8000/health
- API 문서: http://localhost:8000/docs

### 프런트엔드 (로컬)
```bash
cd frontend
npm install
npm run dev
```
- 개발 서버: http://localhost:5173

### 환경 변수 설정

#### Backend (`.env`)
```bash
# AI API (필수)
GEMINI_API_KEY=your_gemini_api_key_here

# Database (기본값: SQLite, 프로덕션: PostgreSQL)
DATABASE_URL=sqlite:///./local.db
# PostgreSQL 예시:
# DATABASE_URL=postgresql://user:password@localhost:5432/rokey_news

# CORS (프론트엔드 URL)
ALLOWED_ORIGINS=http://localhost:5173
# 여러 개: ALLOWED_ORIGINS=http://localhost:5173,https://your-frontend.com

# Rate Limiting
RATE_LIMIT_PER_MIN=60

# RSS Sources (JSON 배열)
RSS_SOURCES=[{"name":"Example","url":"https://example.com/rss"}]
```

#### Frontend (`.env`)
```bash
VITE_API_BASE_URL=http://localhost:8000
```

## 주요 기능

### 구현 완료
- ✅ RSS 수집 및 중복 방지(해시 기반)
- ✅ Gemini 기반 요약/감성 분석/키워드 추출
- ✅ 기사 목록 조회 (검색, 감성 필터, 출처 필터, 날짜 필터, 정렬)
- ✅ 기사 상세 보기
- ✅ 감성 분석 결과 시각화 (긍정/중립/부정)
- ✅ CI/CD: GitHub Actions (lint, build, test, deploy)
- ✅ Render.com 배포 (PostgreSQL + Web Service + Static Site)

### 향후 개선 사항
- 📝 사용자 인증 및 권한 관리
- 📝 기사 북마크 및 즐겨찾기
- 📝 실시간 RSS 업데이트 (웹소켓/SSE)
- 📝 대시보드 및 통계 (감성 트렌드, 키워드 분석)
- 📝 다국어 지원

## API 엔드포인트

### Health Check
- `GET /health` - 서버 상태 확인

### Articles
- `GET /articles` - 기사 목록 조회
  - Query params: `q` (검색어), `sentiment` (positive/neutral/negative), `source` (출처), `from`/`to` (날짜), `sort` (정렬)
- `GET /articles/{id}` - 기사 상세 조회
- `GET /articles/{id}/analysis` - 기사 분석 결과 조회

### Analyses
- `GET /analyses/{id}` - 분석 결과 조회

### Admin
- `POST /admin/ingest/run` - RSS 수집 및 분석 실행

자세한 API 문서는 `http://localhost:8000/docs`에서 확인하세요.

## 배포 (Render.com)

### 배포 아키텍처
- **Database**: PostgreSQL (Render Managed Database)
- **Backend**: Web Service (Python)
- **Frontend**: Static Site

### 환경 변수 (Render)

#### Backend Web Service
```
GEMINI_API_KEY=your_key
DATABASE_URL=<Render PostgreSQL Internal URL>
ALLOWED_ORIGINS=https://your-frontend.onrender.com
RATE_LIMIT_PER_MIN=60
RSS_SOURCES=[{"name":"Example","url":"https://example.com/rss"}]
```

#### Frontend Static Site
```
VITE_API_BASE_URL=https://your-backend.onrender.com
```

자세한 배포 가이드는 `docs/deploy-guide.md`를 참조하세요.

## 트러블슈팅

### 1. Backend: psycopg2 ModuleNotFoundError
**증상**: `ModuleNotFoundError: No module named 'psycopg2'`

**원인**: Render의 DATABASE_URL이 `postgresql://`로 시작할 때 SQLAlchemy가 psycopg2를 찾으려 함

**해결**: `backend/app/database.py`에서 URL을 `postgresql+psycopg://`로 변환 (이미 구현됨)

### 2. Frontend: CORS Error
**증상**: `Access-Control-Allow-Origin header is present on the requested resource`

**원인**: Backend의 `ALLOWED_ORIGINS`에 프론트엔드 URL이 포함되지 않음

**해결**: Render 백엔드 환경 변수에서 `ALLOWED_ORIGINS`를 프론트엔드 URL로 설정
```
ALLOWED_ORIGINS=https://your-frontend.onrender.com
```

### 3. Backend: AttributeError '_GeneratorContextManager'
**증상**: `'_GeneratorContextManager' object has no attribute 'query'`

**원인**: FastAPI Depends와 `@contextmanager` 데코레이터 충돌

**해결**: `get_db()` 함수에서 `@contextmanager` 제거 (이미 수정됨)

### 4. Backend: SQL Syntax Error (DESC NULLS LAST)
**증상**: `syntax error at or near "DESC"`

**원인**: `desc(column.nullslast())` 순서 오류

**해결**: `desc(column).nullslast()` 순서로 변경 (이미 수정됨)

### 5. CI: pytest import error
**증상**: `ModuleNotFoundError: No module named 'app'`

**원인**: pytest가 프로젝트 루트에서 실행되어 `backend` 디렉토리를 찾지 못함

**해결**: `.github/workflows/ci-backend.yml`에 `working-directory: backend` 추가 (이미 수정됨)

## 로컬 개발 팁

### 데이터베이스 마이그레이션
```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### 테스트 실행
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run lint
npm run build
```

### RSS 수집 및 분석 실행
```bash
# API 호출
curl -X POST http://localhost:8000/admin/ingest/run

# 또는 브라우저에서 http://localhost:8000/docs 접속 후 실행
```

## GitHub Actions 시크릿 설정

다음 시크릿을 GitHub Repository Settings > Secrets에 추가하세요:

### 배포용
- `RENDER_API_KEY` - Render API Key
- `RENDER_SERVICE_ID` - Backend Web Service ID
- `RENDER_STATIC_ID` - Frontend Static Site ID

### 추가 환경 변수
- `GEMINI_API_KEY` - Gemini API Key (선택, 테스트용)

## 참고 문서
- 상세 기획/설계: `docs/requirements.md`, `docs/architecture.md`
- API 프롬프트: `docs/prompt-spec.md`
- 프론트엔드 계획: `docs/frontend-plan.md`
- 백엔드 계획: `docs/backend-plan.md`
- CI/CD 설정: `docs/ci-cd.md`
- **배포 가이드**: `docs/deploy-guide.md`

## 라이센스
MIT License

## 기여
Pull Request를 환영합니다!
