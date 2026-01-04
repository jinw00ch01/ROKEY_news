# 프런트엔드 설계 (React + Vite + TS)

## 스택
- Vite + React + TypeScript
- 스타일: TailwindCSS 예정(추가 설치 필요)
- 상태/데이터 패칭: React Query(또는 경량 fetch 훅) 예정
- 라우팅: React Router

## 주요 화면
- `/`: 기사 목록 + 필터(감성, 날짜, 출처) + 검색바 + 정렬(최근/감성점수)
- `/article/:id`: 요약, 감성 라벨/점수, 키워드, 원문 링크
- `/health`: (내부용) 백엔드 상태 표시 또는 숨김

## 컴포넌트 초안
- `Layout`: 헤더(검색/필터), 푸터.
- `ArticleList`: 카드 렌더, 무한 스크롤 또는 페이지네이션.
- `Filters`: 감성 라디오, 날짜 범위, 출처 드롭다운.
- `SortSelect`: 최신순/감성점수순.
- `ArticleCard`: 제목, 출처, 발행일, 감성 배지, 요약 미리보기.
- `ArticleDetail`: 본문 요약, 감성, 키워드 태그, 원문 링크.
- `Skeleton/EmptyState/ErrorState`: 로딩/빈/오류 UI.

## API 연동 패턴
- 클라이언트 래퍼: `api.ts`에 `getArticles(params)`, `getArticle(id)`, `getAnalysis(id)`.
- DTO 매핑: 감성 라벨 → 뱃지 색, 점수 → 게이지.
- 에러 처리: 429/5xx 재시도(React Query), 4xx는 메시지 표시.

## 상태/필터
- URL 쿼리동기화: `?q=...&sentiment=positive&from=...&source=...&sort=score`.
- 전역 최소화, 나머지는 서버 데이터 캐시 활용.

## 접근성/국제화
- 키보드 내비게이션, aria-label/role 준수.
- 텍스트 언어 한국어 기본, 영어 뉴스도 렌더 가능.

## 테스트
- 유닛: 필터 상태 훅, 정렬 함수.
- 통합: 목록 API 모킹, 필터 적용 후 결과 개수 검증.
- 비주얼: 핵심 페이지 스냅샷.

## 스타일 가이드
- 색상 토큰: 감성별 배지(positive/neutral/negative) 정의.
- 타이포/간격 일관성 유지(Tailwind 프리셋 활용).

