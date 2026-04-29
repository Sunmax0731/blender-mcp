from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class OpenAICompatibleConfig:
    base_url: str
    api_key: str
    model: str
    timeout_seconds: float


def load_openai_compatible_config() -> OpenAICompatibleConfig:
    return OpenAICompatibleConfig(
        base_url=os.getenv("BLENDER_MCP_OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/"),
        api_key=os.getenv("BLENDER_MCP_OPENAI_API_KEY", "").strip(),
        model=os.getenv("BLENDER_MCP_OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini",
        timeout_seconds=float(os.getenv("BLENDER_MCP_OPENAI_TIMEOUT_SECONDS", "30")),
    )
