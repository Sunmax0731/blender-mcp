from __future__ import annotations

from collections.abc import Mapping

import httpx

from .ai_config import OpenAICompatibleConfig


class OpenAICompatibleError(Exception):
    def __init__(self, code: str, message: str, *, retryable: bool = False):
        super().__init__(message)
        self.code = code
        self.message = message
        self.retryable = retryable


def create_chat_completion(
    *,
    config: OpenAICompatibleConfig,
    user_prompt: str,
    system_prompt: str,
    temperature: float = 0.2,
    client: httpx.Client | None = None,
) -> dict[str, object]:
    if not config.api_key:
        raise OpenAICompatibleError(
            "AI_PROVIDER_NOT_CONFIGURED",
            "OpenAI compatible API key is not configured.",
            retryable=False,
        )

    payload = {
        "model": config.model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
    }
    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json",
    }

    own_client = client is None
    http_client = client or httpx.Client(timeout=config.timeout_seconds)
    try:
        response = http_client.post(
            f"{config.base_url}/chat/completions",
            json=payload,
            headers=headers,
        )
    except httpx.TimeoutException as exc:
        raise OpenAICompatibleError(
            "AI_PROVIDER_TIMEOUT",
            "OpenAI compatible API request timed out.",
            retryable=True,
        ) from exc
    except httpx.HTTPError as exc:
        raise OpenAICompatibleError(
            "AI_PROVIDER_CONNECTION_ERROR",
            f"OpenAI compatible API request failed: {exc}",
            retryable=True,
        ) from exc
    finally:
        if own_client:
            http_client.close()

    if response.status_code >= 400:
        message = _extract_error_message(response)
        retryable = response.status_code >= 500 or response.status_code == 429
        raise OpenAICompatibleError(
            "AI_PROVIDER_ERROR",
            message,
            retryable=retryable,
        )

    body = response.json()
    content = _extract_message_content(body)
    return {
        "provider": "openai-compatible",
        "model": body.get("model", config.model),
        "content": content,
        "raw": body,
    }


def _extract_error_message(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return f"OpenAI compatible API returned HTTP {response.status_code}."
    error_payload = payload.get("error", {})
    if isinstance(error_payload, Mapping):
        message = error_payload.get("message")
        if isinstance(message, str) and message:
            return message
    return f"OpenAI compatible API returned HTTP {response.status_code}."


def _extract_message_content(payload: Mapping[str, object]) -> str:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise OpenAICompatibleError(
            "AI_PROVIDER_ERROR",
            "OpenAI compatible API response does not contain choices.",
            retryable=False,
        )
    first_choice = choices[0]
    if not isinstance(first_choice, Mapping):
        raise OpenAICompatibleError(
            "AI_PROVIDER_ERROR",
            "OpenAI compatible API response choice is invalid.",
            retryable=False,
        )
    message = first_choice.get("message")
    if not isinstance(message, Mapping):
        raise OpenAICompatibleError(
            "AI_PROVIDER_ERROR",
            "OpenAI compatible API response message is missing.",
            retryable=False,
        )
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, Mapping) and item.get("type") == "text":
                text_value = item.get("text")
                if isinstance(text_value, str):
                    text_parts.append(text_value)
        if text_parts:
            return "\n".join(text_parts)
    raise OpenAICompatibleError(
        "AI_PROVIDER_ERROR",
        "OpenAI compatible API response content is missing.",
        retryable=False,
    )
