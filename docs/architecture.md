# 아키텍처 및 데이터 모델 설계

## 컴포넌트 개요
- **Fetcher**: finnhub 및 NEWSDATA.io API 호출, 뉴스 데이터 수집, 중복/변경 감지, 큐에 적재.
- **Preprocessor**: HTML 제거·정규화, 길이 제한, 안전 필터.
- **Analyzer**: Gemini 호출로 요약/감성/키워드 생성, JSON 스키마 검증.
- **API(FastAPI)**: 기사/분석 조회, 수집 트리거, 헬스 체크.
- **DB**: 개발 SQLite, 배포 Postgres 호환 스키마.
- **Web(React)**: 목록/필터/상세/검색 UI.

```mermaid
flowchart TD
  finnhub[finnhub API] --> fetcher[Fetcher]
  newsdata[NEWSDATA.io API] --> fetcher
  fetcher --> preprocess[Preprocessor]
  preprocess --> analyzer[Analyzer(Gemini)]
  analyzer --> db[(DB)]
  db --> api[FastAPI API]
  api --> web[React Web]
```

## 데이터 모델
- `sources`: `id PK`, `name`, `api_type (finnhub/newsdata)`, `active`, `last_fetched_at`.
- `articles`: `id PK`, `source_id FK`, `title`, `link`, `published_at`, `content_raw`, `content_clean`, `hash`, `created_at`.
- `analyses`: `id PK`, `article_id FK`, `summary`, `sentiment_label (pos/neu/neg)`, `sentiment_score (-1..1)`, `keywords JSON`, `json_meta JSON`, `model_name`, `created_at`.
- 인덱스: `articles.hash`(중복 방지), `articles.published_at`, `analyses.sentiment_label`, `analyses.sentiment_score`.

## 시퀀스
1) **수집**: 스케줄러/수동 → Fetcher가 API 호출 → 새/갱신 기사만 큐.
2) **정규화**: Preprocessor가 본문 추출·클린 → 길이 제한·PPI/금칙어 검출.
3) **분석**: Analyzer가 Gemini 호출 → JSON 스키마 검증 → DB 저장.
4) **노출**: API `GET /articles`, `GET /articles/{id}`, `GET /analyses/{id}` → 웹 UI.

## 에러/재시도
- Fetcher: API 호출 실패 시 로그 후 백오프(예: 1m, 5m, 15m).
- Analyzer: 모델 호출 429/5xx 시 지수 백오프+최대 시도 3회, 폴백(이전 요약/간이 규칙).
- API 응답 파싱 실패/스키마 불일치: 해당 기사만 격리 저장(`json_meta.error`).

## 보안/안전
- 입력 길이 제한(예: 8k chars) 후 모델 호출.
- API 키 보안: .env 파일 사용, 환경 변수로 관리.
- CORS: 프런트 도메인 허용.
- 로그: PII 마스킹, 모델 프롬프트/응답 전문 저장 금지(요약형 메타).

## 모니터링
- 메트릭: 수집 성공/실패, 모델 응답 시간, 감성 라벨 분포, 큐 길이.
- 알림: 임계치 초과 시 이메일/웹훅.

## 설정/환경 변수(예시)
- `GEMINI_API_KEY`, `FINNHUB_API_KEY`, `NEWSDATA_API_KEY`, `DATABASE_URL`, `RATE_LIMIT_PER_MIN`, `ALLOWED_ORIGINS`.
