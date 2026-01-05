# 진행 현황 요약

> 이 문서는 프로젝트의 현재 상태를 추적합니다.

## 완료된 항목

### 백엔드
- ✅ 기본 스캐폴드: 설정 로더(`config.py`), 모델 정의(`models.py`), 스키마(`schemas.py`)
- ✅ finnhub & NEWSDATA.io API 통합 (`services/news_fetcher.py`)
- ✅ Gemini 분석 클라이언트 (`services/analyzer.py`)
- ✅ 파이프라인 오케스트레이션 (`services/pipeline.py`)
- ✅ API 라우트: `/health`, `/articles`, `/articles/{id}`, `/analyses/{id}`, `/admin/ingest/run`
- ✅ 데이터베이스: SQLAlchemy + Alembic 마이그레이션
- ✅ 입력 정제: HTML 정리, 텍스트 클리닝
- ✅ API 키 기반 뉴스 수집 (RSS 제거)

### 프런트엔드
- ✅ 기본 UI: Tailwind CSS + React Router + React Query
- ✅ 기사 목록 페이지 (필터, 검색, 정렬)
- ✅ 기사 상세 페이지
- ✅ 감성 분석 결과 시각화
- ✅ API 클라이언트 래퍼

### 배포 & CI/CD
- ✅ GitHub Actions: 프런트 lint·build, 백엔드 pytest
- ✅ Render.com 배포: PostgreSQL + Web Service + Static Site
- ✅ 환경 변수 설정 (Render.com)
- ✅ CORS 설정

### 문서
- ✅ README.md (finnhub/NEWSDATA.io 기반)
- ✅ 기획서 (docs/requirements.md)
- ✅ 아키텍처 설계 (docs/architecture.md)
- ✅ 백엔드 계획 (docs/backend-plan.md)
- ✅ 프론트엔드 계획 (docs/frontend-plan.md)
- ✅ Gemini 프롬프트 명세 (docs/prompt-spec.md)
- ✅ 배포 가이드 (docs/deploy-guide.md)

## 현재 구조

### 데이터 소스
- **finnhub API**: 일반 뉴스 카테고리
- **NEWSDATA.io API**: 한국 뉴스 (언어: ko, 국가: kr)

### 데이터 흐름
```
finnhub API ──┐
              ├──> Fetcher ──> Preprocessor ──> Gemini Analyzer ──> DB ──> FastAPI ──> React
NEWSDATA.io ──┘
```

## 향후 개선 사항

### 기능
- 📝 사용자 인증 및 권한 관리
- 📝 기사 북마크 및 즐겨찾기
- 📝 실시간 뉴스 업데이트 (웹소켓/SSE)
- 📝 대시보드 및 통계 (감성 트렌드, 키워드 분석)
- 📝 다국어 지원
- 📝 뉴스 카테고리별 필터링 (경제, 기술, 정치 등)
- 📝 알림 기능 (특정 키워드/감성 기준)

### 기술
- 📝 레이트 리밋 고도화 (토큰 버킷/세마포어)
- 📝 구조화된 로깅 (JSON 포맷)
- 📝 에러 추적 (Sentry 등)
- 📝 모니터링 (메트릭, 알림)
- 📝 캐싱 (Redis)
- 📝 테스트 커버리지 확대

### 문서
- 📝 API 문서 자동화 (OpenAPI/Swagger 주석 확대)
- 📝 기여 가이드
- 📝 트러블슈팅 가이드 확장

## 알려진 이슈
- Source 모델 변경으로 기존 DB 마이그레이션 필요
- finnhub 무료 플랜은 호출 제한이 있음 (60 calls/minute)
- NEWSDATA.io 무료 플랜은 200 credits/day

## API 키 관리
모든 API 키는 Render.com 환경 변수로 관리:
- `GEMINI_API_KEY`
- `FINNHUB_API_KEY`
- `NEWSDATA_API_KEY`
- `DATABASE_URL` (Render PostgreSQL)
- `ALLOWED_ORIGINS` (프론트엔드 URL)
