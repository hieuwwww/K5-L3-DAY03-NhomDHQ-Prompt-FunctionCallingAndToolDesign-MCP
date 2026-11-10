from __future__ import annotations

import os

from providers.openai_provider import OpenAIProvider


class DeepSeekProvider(OpenAIProvider):
    """DeepSeek uses an OpenAI-compatible Chat Completions surface.

    DeepSeek models run in "thinking" mode by default, and thinking mode rejects
    tool_choice="required" (HTTP 400), which run_eval.py sends for every case that
    expects a tool call. So thinking is disabled unless DEEPSEEK_THINKING=enabled.
    """

    def __init__(self) -> None:
        thinking = os.getenv("DEEPSEEK_THINKING", "disabled").strip().lower()
        super().__init__(
            api_key_env="DEEPSEEK_API_KEY",
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            default_model=os.getenv("DEEPSEEK_MODEL", "deepseek-flash"),
            extra_body={"thinking": {"type": "enabled" if thinking == "enabled" else "disabled"}},
        )
