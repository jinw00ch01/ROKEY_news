# 백엔드 설계 (FastAPI)

## 목표
- RSS 수집 → 정규화 → Gemini 분석 → 저장 → 조회 API 제공.
- 개발: SQLite, 배포: Postgres 호환 유지.

## 모듈 구조 초안
- `app/main.py`: FastAPI 엔트리, 라우터 등록, CORS.
- `app/config.py`: env 로딩(`GEMINI_API_KEY`, `DATABASE_URL`, `ALLOWED_ORIGINS`, `RATE_LIMIT_PER_MIN` 등).
- `app/models.py`: SQLAlchemy 모델(sources, articles, analyses).
- `app/schemas.py`: Pydantic 응답/요청.
- `app/services/rss.py`: RSS fetch/parse, 중복 해시.
- `app/services/analyzer.py`: Gemini 호출, JSON 검증.
- `app/services/pipeline.py`: 수집→정규화→분석 오케스트레이션.
- `app/routes/articles.py`: 목록/상세/필터.
- `app/routes/admin.py`: 수집 트리거, 헬스.

## 핵심 엔드포인트
- `GET /health`: 상태 OK.
- `POST /ingest/run`: 수집/분석 파이프라인 수동 실행(관리용).
- `GET /articles`: 필터 `q, sentiment, source, from, to, sort` 지원.
- `GET /articles/{id}`: 기사+요약+감성 포함 조회 또는 `analysis` 분리 제공.
- `GET /analyses/{id}`: 분석만 단독 조회.

## 처리 플로우
1) RSS fetch → 새 링크 해시 확인 → 원문 fetch(필요 시).
2) 본문 정규화: HTML 제거, 길이 제한, 안전 키워드 검사.
3) Gemini 호출(프롬프트: `docs/prompt-spec.md`) → JSON 검증.
4) DB 저장: articles, analyses 업서트.

## 데이터 접근/인덱스
- `articles.hash` 유니크 인덱스(중복 방지).
- `articles.published_at` 역순 정렬 기본.
- `analyses.sentiment_label/score` 인덱스(필터/정렬).

## 의존 패키지 제안
- `fastapi`, `uvicorn[standard]`
- `sqlalchemy` + `alembic` (마이그레이션)
- `httpx` (비동기 fetch)
- `feedparser` (RSS)
- `python-dotenv` (개발 env)

## 안정성/레이트 리밋
- Gemini 호출: 분당 호출 제한 값 주입, 토큰 버킷/세마포어로 제어.
- 백오프: 429/5xx 시 지수 백오프, 최대 3회.

## 로깅/메트릭
- 구조화 로그(JSON): source, article_id, status, duration.
- 메트릭 훅: 성공/실패 카운터, 분석 지연, 모델 호출 시간.

## 테스트 전략
- 파서 단위 테스트: RSS → normalized content.
- 서비스 통합: mock Gemini 응답으로 파이프라인 검증.
- API 테스트: 필터/정렬 파라미터 동작, 404/400 처리.

