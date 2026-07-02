import json
import os
import re
from typing import Any, Dict
from urllib import error, parse, request


class LLMClientError(RuntimeError):
    pass


def gemini_is_enabled() -> bool:
    return bool(os.getenv("GEMINI_API_KEY"))


def _extract_json_object(text: str) -> Dict[str, Any]:
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.IGNORECASE | re.DOTALL)
    if match:
        text = match.group(1)
    else:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1]

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise LLMClientError(f"Could not parse JSON from model output: {exc}") from exc


def call_gemini_json(prompt: str, *, model: str = None, temperature: float = 0.2, max_output_tokens: int = 768) -> Dict[str, Any]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise LLMClientError("GEMINI_API_KEY is not set")

    model_name = model or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    url = "https://generativelanguage.googleapis.com/v1beta/models/" + parse.quote(model_name, safe="") + ":generateContent?key=" + parse.quote(api_key, safe="")
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_output_tokens,
        },
    }

    req = request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=30) as resp:
            response_payload = json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="ignore")
        raise LLMClientError(f"Gemini HTTP error {exc.code}: {error_body}") from exc
    except error.URLError as exc:
        raise LLMClientError(f"Gemini request failed: {exc.reason}") from exc

    candidates = response_payload.get("candidates") or []
    if not candidates:
        raise LLMClientError("Gemini returned no candidates")

    content = candidates[0].get("content") or {}
    parts = content.get("parts") or []
    text = "".join(part.get("text", "") for part in parts if isinstance(part, dict))
    if not text.strip():
        raise LLMClientError("Gemini returned an empty response")

    return _extract_json_object(text)