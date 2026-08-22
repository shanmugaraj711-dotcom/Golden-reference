from __future__ import annotations

import json
import os
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .model_provider import ModelRequest, ModelResponse


@dataclass
class GeminiProvider:
    """Server-side Gemini API adapter using only the standard library.

    The API key is read from GEMINI_API_KEY and never stored in the repository.
    The model defaults to the current free-tier model exposed by the runtime.
    """

    api_key: str | None = None
    model: str | None = None
    timeout_seconds: int = 90
    name: str = "gemini"
    estimated_request_cost: float = 0.0

    def __post_init__(self) -> None:
        self.api_key = self.api_key or os.getenv("GEMINI_API_KEY")
        self.model = self.model or os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    def is_local(self) -> bool:
        return False

    def estimated_cost(self, request: ModelRequest) -> float:
        return self.estimated_request_cost

    def available(self) -> bool:
        return bool(self.api_key)

    def complete(self, request: ModelRequest) -> ModelResponse:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")

        system = request.context.get("system", "You are the Project Factory AI worker.")
        payload = {
            "system_instruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": request.instruction}]}],
            "generationConfig": {"temperature": 0},
        }
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent"
        )
        req = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key,
            },
            method="POST",
        )
        try:
            with urlopen(req, timeout=self.timeout_seconds) as response:
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[-2000:]
            raise RuntimeError(f"Gemini API request failed ({exc.code}): {detail}") from exc
        except (OSError, URLError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Gemini API request failed: {exc}") from exc

        try:
            parts = data["candidates"][0]["content"]["parts"]
            output = "".join(str(part.get("text", "")) for part in parts)
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("Gemini returned an invalid generateContent response") from exc

        usage = data.get("usageMetadata") or {}
        return ModelResponse(
            provider=self.name,
            model=self.model or "unknown",
            output=output,
            input_tokens=int(usage.get("promptTokenCount", 0) or 0),
            output_tokens=int(usage.get("candidatesTokenCount", 0) or 0),
            estimated_cost=self.estimated_request_cost,
        )
