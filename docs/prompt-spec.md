# Gemini 프롬프트 명세

## 공통 가드레일
- 입력: 정제된 한국어 본문, 길이 제한(예: 8000자).
- 금칙: 개인정보/계좌/주민번호/연락처 발견 시 `"safety_flag": true`와 사유를 반환.
- 출력은 항상 JSON; 추가 자연어 금지.
- 톤: 중립, 과장 금지, 추측/투자 조언 금지.

## 요청 스키마(예시)
```json
{
  "article": {
    "title": "string",
    "content": "string",
    "published_at": "ISO8601",
    "source": "string"
  },
  "need_keywords": true
}
```

## 응답 스키마(기대)
```json
{
  "summary": "3-4문장 한국어 요약",
  "sentiment": {
    "label": "positive|neutral|negative",
    "score": -1.0
  },
  "keywords": ["키워드1", "키워드2"],
  "reason": "라벨 근거 1문장",
  "safety_flag": false,
  "safety_reason": ""
}
```

## 요약+감성+키워드 통합 프롬프트
```
당신은 한국어 뉴스 요약/감성 분석기입니다.
입력은 JSON입니다. 출력은 JSON만 반환하세요.
요약: 3~4문장, 수치/주체 포함, 중립적 서술.
감성: positive/neutral/negative 중 하나로 분류, -1..1 점수.
키워드: 핵심 명사/표현 3~6개.
안전: 개인정보/민감 표현 발견 시 safety_flag=true와 사유를 적으세요.
```

## 실패/폴백 전략
- 429/5xx → 재시도(백엔드 레이어).
- JSON 파싱 실패 → 재요청 시 `Return JSON only` 주입.
- safety_flag=true → UI에서 차단/마스킹, 로그만 저장.

## 샘플 입력/출력
```json
// 입력
{
  "article": {
    "title": "A사 2분기 실적 발표",
    "content": "A사는 2분기 매출 1조원, 영업이익 1200억원...",
    "published_at": "2026-01-03T09:00:00Z",
    "source": "Example News"
  },
  "need_keywords": true
}
```
```json
// 출력
{
  "summary": "A사는 2분기 매출 1조원, 영업이익 1200억원으로 전년 대비 성장했다. ...",
  "sentiment": { "label": "positive", "score": 0.35 },
  "keywords": ["2분기 실적", "매출 1조", "영업이익"],
  "reason": "실적 개선과 매출 성장으로 긍정적 정서가 우세",
  "safety_flag": false,
  "safety_reason": ""
}
```

