import os
import json
import requests
from typing import List, Dict, Any, Tuple

from app.config import MINIMAL_SYSTEM_PROMPT, MODEL, OLLAMA_URL


def _extract_json_from_text(text: str) -> Any:
    try:
        return json.loads(text)
    except Exception:
        pass
    try:
        import re
        match = re.search(r"(\{[\s\S]*\})", text)
        if match:
            return json.loads(match.group(1))
    except Exception:
        pass
    return None


def call_llm_with_issues(issues: List[Dict[str, Any]], timeout: int = 30) -> Tuple[bool, Any]:
    payload = json.dumps({"issues": issues}, ensure_ascii=False, indent=2)
    if os.environ.get("MOCK_OLLAMA") == "1":
        return True, {"issues": issues}

    try:
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": MINIMAL_SYSTEM_PROMPT},
                    {"role": "user", "content": payload},
                ],
                "stream": False,
            },
            timeout=timeout,
        )
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        return False, {"error": str(e)}

    text = resp.text
    parsed = _extract_json_from_text(text)
    if isinstance(parsed, dict):
        message = parsed.get("message")
        if isinstance(message, dict) and isinstance(message.get("content"), str):
            content_json = _extract_json_from_text(message["content"])
            if isinstance(content_json, dict):
                return True, content_json
        return True, parsed

    return False, {"error": "Invalid LLM response", "raw": text}
