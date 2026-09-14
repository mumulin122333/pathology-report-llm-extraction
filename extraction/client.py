"""Minimal client for an OpenAI-compatible chat-completions endpoint."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


class ChatCompletionsClient:
    def __init__(
        self,
        *,
        base_url: str,
        served_model: str,
        api_key: str | None = None,
        timeout: float = 600,
        max_tokens: int = 4000,
        temperature: float = 0.0,
        seed: int = 0,
        extra_body: dict[str, Any] | None = None,
    ) -> None:
        self.endpoint = f"{base_url.rstrip('/')}/chat/completions"
        self.served_model = served_model
        self.api_key = api_key
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.seed = seed
        self.extra_body = extra_body or {}

    def complete(self, messages: list[dict[str, str]]) -> str:
        payload: dict[str, Any] = {
            "model": self.served_model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "seed": self.seed,
            **self.extra_body,
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"endpoint returned HTTP {error.code}: {detail}") from error
        except urllib.error.URLError as error:
            raise RuntimeError(f"could not reach {self.endpoint}: {error.reason}") from error

        try:
            message = body["choices"][0]["message"]
        except (KeyError, IndexError, TypeError) as error:
            raise RuntimeError("endpoint response did not contain a chat completion") from error
        content = message.get("content") or message.get("reasoning_content") or ""
        if not content:
            raise RuntimeError("model returned an empty response")
        return str(content)
