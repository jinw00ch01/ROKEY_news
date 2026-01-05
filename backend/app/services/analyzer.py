from __future__ import annotations

import json
import logging
import re
import time
from collections import deque
from typing import Any, Deque

import httpx

from app.config import get_settings
from app.schemas import AnalyzeRequest, AnalysisResult

logger = logging.getLogger(__name__)

# Use v1 API with gemini-2.5-flash model (1.5 models are retired as of 2026)
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent"
)


class AnalyzerClient:
    _calls: Deque[float] = deque()

    def __init__(self, api_key: str | None = None):
        settings = get_settings()
        self.api_key = api_key or settings.gemini_api_key
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY not configured")
        self.rate_limit_per_min = settings.rate_limit_per_min

    def _build_prompt(self, request: AnalyzeRequest) -> str:
        return (
            "당신은 한국어 뉴스 요약/감성 분석기입니다.\n"
            "입력된 뉴스 기사를 분석하고, 아래의 **정확한 JSON 형식**으로만 응답하세요.\n\n"
            "**중요: 반드시 영어 필드명을 사용하고, 아래 예제와 동일한 구조로 응답해야 합니다.**\n\n"
            "출력 JSON 형식:\n"
            "{\n"
            '  "summary": "3-4문장의 요약 (수치와 주체 포함, 중립적 서술)",\n'
            '  "sentiment": {\n'
            '    "label": "positive 또는 neutral 또는 negative 중 하나",\n'
            '    "score": -1.0에서 1.0 사이의 숫자\n'
            '  },\n'
            '  "keywords": ["키워드1", "키워드2", "키워드3"],\n'
            '  "reason": "이 감성 점수를 부여한 이유",\n'
            '  "safety_flag": false,\n'
            '  "safety_reason": ""\n'
            "}\n\n"
            "규칙:\n"
            "1. 감성 label은 반드시 'positive', 'neutral', 'negative' 중 하나\n"
            "2. 감성 score는 -1.0 ~ 1.0 범위의 숫자 (positive: 0.3~1.0, neutral: -0.3~0.3, negative: -1.0~-0.3)\n"
            "3. keywords는 핵심 명사/표현 3~6개를 배열로\n"
            "4. reason은 반드시 문자열로 제공 (빈 문자열이라도 \"\"로 제공)\n"
            "5. safety_flag는 개인정보/민감 표현 발견 시 true, 아니면 false\n"
            "6. safety_reason은 safety_flag가 true일 때만 내용 작성, 아니면 빈 문자열 \"\"\n"
            "7. 절대 한글 필드명을 사용하지 마세요 (요약 X, summary O)\n"
            "8. **중요: summary, reason 등의 텍스트에 큰따옴표(\")가 포함될 경우 반드시 작은따옴표(')로 대체하세요**\n"
            '   예: "그는 "안녕"이라고 말했다" (X) → "그는 \'안녕\'이라고 말했다" (O)\n\n'
            f"입력 기사:\n{request.model_dump_json()}"
        )

    async def analyze(self, request: AnalyzeRequest) -> AnalysisResult:
        self._respect_rate_limit()
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": self._build_prompt(request)},
                    ]
                }
            ]
        }
        params = {"key": self.api_key}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(GEMINI_URL, params=params, json=payload)
            resp.raise_for_status()
            data = resp.json()

        text = _extract_text(data)
        logger.info(f"Raw Gemini response: {text[:500]}")  # Log first 500 chars

        # Strip markdown code blocks if present
        text = _strip_markdown_json(text)

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON. Response text: {text}")
            raise ValueError(f"Invalid JSON response from Gemini: {e}") from e

        return AnalysisResult(**parsed)

    def _respect_rate_limit(self) -> None:
        # 간단한 토큰 버킷: 1분 윈도우에서 설정된 호출 수를 초과하면 대기
        now = time.time()
        window = 60.0
        while self._calls and now - self._calls[0] > window:
            self._calls.popleft()
        if len(self._calls) >= self.rate_limit_per_min:
            sleep_time = window - (now - self._calls[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        self._calls.append(time.time())


def _extract_text(response_json: dict[str, Any]) -> str:
    try:
        return response_json["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as exc:
        raise ValueError("Unexpected Gemini response shape") from exc


def _strip_markdown_json(text: str) -> str:
    """Remove markdown code block markers from JSON response."""
    # Remove ```json ... ``` or ``` ... ``` blocks
    text = text.strip()
    if text.startswith("```"):
        # Find the first newline after the opening ```
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1:]
        # Remove the closing ```
        if text.endswith("```"):
            text = text[:-3]
    return text.strip()
