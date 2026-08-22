from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.error import URLError
from urllib.request import Request, urlopen

from .model_provider import ModelRequest, ModelResponse


@dataclass
class OpenAICompatibleLocalProvider:
    """Provider for a self-hosted OpenAI-compatible model endpoint.

    The model weights stay outside GitHub. GitHub stores the provider code and
    configuration contract; an approved runtime hosts the weights and exposes
    this private endpoint. No third-party API key is required by this adapter.
    """

    endpoint: str = "http://127.0.0.1:11434/v1/chat/completions"
    health_endpoint: str = "http://127.0.0.1:11434/"
    model: str = "local-coder"
    timeout_seconds: int = 120
    name: str = "local"

    def is_local(self) -> bool:
        return True

    def estimated_cost(self, request: ModelRequest) -> float:
        # No API/token billing for a self-hosted endpoint. Infrastructure cost
        # is tracked separately by the economics layer.
        return 0.0

    def available(self) -> bool:
        try:
            req = Request(self.health_endpoint, method="GET")
            with urlopen(req, timeout=2):
                return True
        except (OSError, URLError):
            return False

    def complete(self, request: ModelRequest) -> ModelResponse:
        messages = [
            {
                "role": "system",
                "content": request.context.get(
                    "system", "You are the Project Factory local coding model."
                ),
            },
            {"role": "user", "content": request.instruction},
        ]
        payload = json.dumps(
            {"model": self.model, "messages": messages, "temperature": 0}
        ).encode()
        req = Request(
            self.endpoint,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(req, timeout=self.timeout_seconds) as response:
                data = json.loads(response.read().decode())
        except (OSError, URLError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Local model request failed: {exc}") from exc

        try:
            output = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                "Local model returned an invalid chat-completions response"
            ) from exc

        usage = data.get("usage") or {}
        return ModelResponse(
            provider=self.name,
            model=data.get("model", self.model),
            output=str(output),
            input_tokens=int(usage.get("prompt_tokens", 0) or 0),
            output_tokens=int(usage.get("completion_tokens", 0) or 0),
            estimated_cost=0.0,
        )
