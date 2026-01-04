import html
import re


def clean_html(text: str, max_len: int = 8000) -> str:
    # 단순 태그 제거 및 공백 정리
    no_tags = re.sub(r"<[^>]+>", " ", text)
    unescaped = html.unescape(no_tags)
    normalized = re.sub(r"\s+", " ", unescaped).strip()
    return normalized[:max_len]

