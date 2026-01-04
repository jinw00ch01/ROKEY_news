from __future__ import annotations

import json
from typing import Any

import httpx

from app.config import get_settings
from app.schemas import AnalyzeRequest, AnalysisResult

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
)


class AnalyzerClient:
    def __init__(self, api_key: str | None = None):
        settings = get_settings()
        self.api_key = api_key or settings.gemini_api_key
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY not configured")

    def _build_prompt(self, request: AnalyzeRequest) -> str:
        return (
            "당신은 한국어 뉴스 요약/감성 분석기입니다.\n"
            "입력은 JSON입니다. 출력은 JSON만 반환하세요.\n"
            "요약: 3~4문장, 수치/주체 포함, 중립적 서술.\n"
            "감성: positive/neutral/negative 중 하나로 분류, -1..1 점수.\n"
            "키워드: 핵심 명사/표현 3~6개.\n"
            "안전: 개인정보/민감 표현 발견 시 safety_flag=true와 사유를 적으세요.\n"
            f"입력 JSON: {request.model_dump_json()}"
        )

    async def analyze(self, request: AnalyzeRequest) -> AnalysisResult:
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
        parsed = json.loads(text)
        return AnalysisResult(**parsed)


def _extract_text(response_json: dict[str, Any]) -> str:
    try:
        return response_json["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as exc:
        raise ValueError("Unexpected Gemini response shape") from exc

