"""Gemini API client with fail-safe logging."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import requests

from partner_os.config import AppConfig
from partner_os.db.store import DataStore


class GeminiAPIError(RuntimeError):
    """Raised when Gemini API calls fail."""


@dataclass(slots=True)
class GeminiClient:
    config: AppConfig
    store: DataStore

    @property
    def endpoint(self) -> str:
        return (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.config.gemini_model}:generateContent"
        )

    def generate_text(self, prompt: str, deal_id: str | None, request_type: str) -> str:
        if not self.config.gemini_api_key:
            self.store.insert_api_call(
                provider="google",
                model=self.config.gemini_model,
                endpoint=self.endpoint,
                request_type=request_type,
                status="failed",
                latency_ms=0,
                deal_id=deal_id,
                error_message="GEMINI_API_KEY is not configured.",
                details={"prompt_excerpt": prompt[:200]},
            )
            raise GeminiAPIError("GEMINI_API_KEY is not configured.")

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "text/plain"},
        }
        params = {"key": self.config.gemini_api_key}

        start = time.perf_counter()
        try:
            response = requests.post(
                self.endpoint,
                headers=headers,
                params=params,
                json=payload,
                timeout=self.config.gemini_timeout_seconds,
            )
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            response.raise_for_status()
            data = response.json()

            candidate = data.get("candidates", [{}])[0]
            parts = candidate.get("content", {}).get("parts", [])
            text = "\n".join(part.get("text", "") for part in parts).strip()
            if not text:
                raise GeminiAPIError("Gemini returned an empty response.")

            usage = data.get("usageMetadata", {})
            self.store.insert_api_call(
                provider="google",
                model=self.config.gemini_model,
                endpoint=self.endpoint,
                request_type=request_type,
                status="success",
                latency_ms=elapsed_ms,
                deal_id=deal_id,
                prompt_tokens=usage.get("promptTokenCount"),
                completion_tokens=usage.get("candidatesTokenCount"),
                total_tokens=usage.get("totalTokenCount"),
                details={"response_id": data.get("responseId", "")},
            )
            return text
        except Exception as exc:  # noqa: BLE001
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.store.insert_api_call(
                provider="google",
                model=self.config.gemini_model,
                endpoint=self.endpoint,
                request_type=request_type,
                status="failed",
                latency_ms=elapsed_ms,
                deal_id=deal_id,
                error_message=str(exc),
                details={"prompt_excerpt": prompt[:200]},
            )
            raise GeminiAPIError(str(exc)) from exc

    def summarize_text(self, text: str, deal_id: str | None) -> str:
        prompt = (
            "Summarize the following real-estate artifact for internal team use. "
            "Return concise bullets: facts, risks, missing data, next actions.\n\n"
            f"{text}"
        )
        return self.generate_text(prompt=prompt, deal_id=deal_id, request_type="summary")

    def chat_reply(self, transcript: list[dict[str, Any]], deal_id: str | None) -> str:
        rendered = "\n".join(f"{item['role']}: {item['content']}" for item in transcript)
        prompt = (
            "You are The Manager in Partner OS. Provide a concise internal response, "
            "prioritizing reliability and explicit next step.\n\n"
            f"{rendered}"
        )
        return self.generate_text(prompt=prompt, deal_id=deal_id, request_type="chat")


@dataclass(slots=True)
class NullLLMClient:
    """Test/client stub that always fails."""

    def summarize_text(self, text: str, deal_id: str | None) -> str:  # noqa: ARG002
        raise GeminiAPIError("LLM unavailable")

    def chat_reply(self, transcript: list[dict[str, Any]], deal_id: str | None) -> str:  # noqa: ARG002
        raise GeminiAPIError("LLM unavailable")
