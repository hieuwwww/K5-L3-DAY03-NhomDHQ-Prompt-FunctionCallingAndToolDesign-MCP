"""Streamlit UI for the Research Agent.

Run from starter_v0/:
    streamlit run app.py

It reuses the multi-round tool loop from chat.py, so the UI behaves exactly like
the CLI chat. Every turn is saved to transcripts/*.transcript.json in the same
format as chat.py, so UI sessions count as live-chat evidence for the report.
"""
from __future__ import annotations

import csv
import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st
import yaml

from chat import ARTIFACTS_DIR, ROOT, now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"
TRANSCRIPTS_DIR = ROOT / "transcripts"

PROVIDERS = ["openrouter", "openai", "anthropic", "gemini", "ollama"]
PROVIDER_KEYS = {
    "openrouter": "OPENROUTER_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "ollama": None,  # local server, no key
}
# These have a working default in the tool code, so a missing value is not a problem.
ENV_WITH_DEFAULT = {"ARXIV_USER_AGENT", "RAPIDAPI_TWITTER_HOST"}

SAMPLE_PROMPTS = [
    "Tin AI hôm nay có gì nổi bật?",
    "Cho mình các tweet phổ biến nhất về Claude",
    "Tóm tắt bài này giúp mình: https://www.anthropic.com/research",
    "Tìm paper arXiv mới về AI agent evaluation",
    "Theo policy công ty, tweet viral có được coi là fact đã xác nhận không?",
    "Tóm tắt 5 tweet mới nhất giúp mình",
]

# The tool loop prints emoji progress lines; avoid UnicodeEncodeError on non-UTF-8 consoles.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass


@dataclass(frozen=True)
class Settings:
    provider: str
    model: str
    version: str
    history_window: int
    max_tool_rounds: int


def load_streamlit_secrets() -> None:
    """On Streamlit Cloud, keys live in st.secrets instead of .env."""
    try:
        if st.secrets.load_if_toml_exists():
            for key, value in st.secrets.items():
                if isinstance(value, str):
                    os.environ.setdefault(key, value)
    except Exception:
        pass


def latest_logged_version() -> str:
    """Default the version label to the last row of version_log.csv."""
    try:
        with (ARTIFACTS_DIR / "version_log.csv").open(encoding="utf-8", newline="") as file:
            versions = [(row.get("version") or "").strip() for row in csv.DictReader(file)]
    except OSError:
        return "v0"
    versions = [v for v in versions if v]
    return versions[-1] if versions else "v0"


def tool_env_requirements() -> dict[str, list[str]]:
    """Read requires_env from each tools/<folder>/TOOL.md, keyed by tool name."""
    requirements: dict[str, list[str]] = {}
    for tool_md in sorted((ROOT / "tools").glob("*/TOOL.md")):
        try:
            front = yaml.safe_load(tool_md.read_text(encoding="utf-8").split("---")[1]) or {}
        except Exception:
            continue
        if front.get("name"):
            requirements[front["name"]] = list(front.get("requires_env") or [])
    return requirements


def start_conversation(settings: Settings) -> None:
    state = st.session_state
    provider = make_provider(settings.provider)
    artifact_version = build_artifact_version(settings.version, SYSTEM_PROMPT_PATH, TOOLS_PATH)
    transcript_id = "_".join([
        safe_slug(settings.version),
        safe_slug(settings.provider),
        "ui",
        datetime.now().strftime("%Y%m%dT%H%M%S%f"),
    ])
    state.settings = settings
    state.provider = provider
    state.system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    state.tool_declarations = load_tool_declarations(TOOLS_PATH)
    state.tools = to_openai_tools(state.tool_declarations)
    state.artifact_version = artifact_version.artifact_version
    state.transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    state.transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": settings.provider,
        "model": settings.model or getattr(provider, "default_model", None),
        "system_prompt": str(SYSTEM_PROMPT_PATH),
        "tools": str(TOOLS_PATH),
        "history_window": settings.history_window,
        "max_tool_rounds": settings.max_tool_rounds,
        "interface": "streamlit",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    state.history = []   # user/assistant text pairs fed back to the model
    state.messages = []  # what the page shows


def run_turn(user_text: str) -> dict[str, Any]:
    """Same steps as one loop iteration of chat.py main()."""
    state = st.session_state
    settings: Settings = state.settings
    turn_record: dict[str, Any] = {
        "turn_index": len(state.transcript["turns"]) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }
    messages = [
        {"role": "system", "content": state.system_prompt},
        *trim_history(state.history, settings.history_window),
        {"role": "user", "content": user_text},
    ]
    try:
        result = run_model_tool_loop(
            provider=state.provider,
            messages=messages,
            tools=state.tools,
            model=settings.model or None,
            max_tool_rounds=settings.max_tool_rounds,
        )
        turn_record.update(result)
        state.history.append({"role": "user", "content": user_text})
        state.history.append({"role": "assistant", "content": result["assistant_text"]})
    except Exception as exc:
        turn_record.update({"status": "provider_error", "error": f"{type(exc).__name__}: {exc}"})
    turn_record["ended_at"] = now_iso()
    state.transcript["turns"].append(turn_record)
    write_transcript(state.transcript_path, state.transcript)
    return turn_record


def render_tool_events(rounds: list[dict[str, Any]]) -> None:
    events = [(item["round"], event) for item in rounds for event in item.get("tool_results", [])]
    if not events:
        return
    st.caption("Tool đã gọi: " + " → ".join(f"`{event['tool']}`" for _, event in events))
    with st.expander(f"Chi tiết {len(events)} tool call (args + kết quả)"):
        for round_no, event in events:
            st.markdown(f"**Vòng {round_no} · `{event['tool']}`**")
            st.code(json.dumps(event.get("args", {}), ensure_ascii=False, indent=2), language="json")
            result = event.get("result")
            if isinstance(result, dict) and result.get("error"):
                st.error(f"{result['error']}: {result.get('message', '')}")
            st.json(result, expanded=False)


def render_assistant(message: dict[str, Any]) -> None:
    render_tool_events(message.get("rounds", []))
    status = message.get("status")
    if status == "provider_error":
        st.error(f"Lỗi khi gọi model: {message.get('error')}")
        return
    st.markdown(message.get("content") or "_(agent không trả lời)_")
    if status == "waiting_for_user":
        st.info("Agent đang hỏi lại, hãy trả lời ở ô chat bên dưới.")
    elif status == "max_tool_rounds":
        st.warning("Agent dừng vì chạm giới hạn số vòng tool.")


def render_sidebar() -> Settings:
    with st.sidebar:
        st.header("Cài đặt")
        provider = st.selectbox("Provider", PROVIDERS, index=0)
        model = st.text_input(
            "Model",
            value="",
            placeholder=getattr(make_provider(provider), "default_model", "") or "",
            help="Để trống = dùng model mặc định của provider.",
        ).strip()
        version = st.text_input(
            "Version label",
            value=latest_logged_version(),
            help="Nhãn phiên bản prompt/tools ghi vào transcript, ví dụ v3.",
        ).strip() or "v0"
        col1, col2 = st.columns(2)
        history_window = int(col1.number_input("History", min_value=0, max_value=20, value=5,
                                               help="Giữ N cặp hỏi/đáp gần nhất làm ngữ cảnh."))
        max_tool_rounds = int(col2.number_input("Max rounds", min_value=1, max_value=8, value=4,
                                                help="Số vòng gọi tool tối đa mỗi lượt."))
        settings = Settings(provider, model, version, history_window, max_tool_rounds)

        if st.button("Cuộc trò chuyện mới", width="stretch"):
            st.session_state.restart = True

        st.divider()
        st.subheader("API key")
        key_name = PROVIDER_KEYS.get(provider)
        if key_name is None:
            st.markdown(f"Model: `{provider}` chạy local, không cần key")
        else:
            st.markdown(f"{'✅' if os.getenv(key_name) else '❌'} Model: `{key_name}`")

        requirements = tool_env_requirements()
        declared = [item["name"] for item in load_tool_declarations(TOOLS_PATH)]
        for name in declared:
            needed = [env for env in requirements.get(name, []) if env not in ENV_WITH_DEFAULT]
            missing = [env for env in needed if not os.getenv(env)]
            if not needed:
                st.markdown(f"✅ `{name}`")
            elif missing:
                st.markdown(f"❌ `{name}` thiếu {', '.join(f'`{env}`' for env in missing)}")
            else:
                st.markdown(f"✅ `{name}`")
        st.caption("Chỉ kiểm tra key có hay không, không hiển thị giá trị.")
    return settings


def render_download() -> None:
    transcript = st.session_state.transcript
    if not transcript["turns"]:
        return
    with st.sidebar:
        st.divider()
        st.download_button(
            "Tải transcript JSON",
            data=json.dumps(transcript, ensure_ascii=False, indent=2, default=str),
            file_name=Path(st.session_state.transcript_path).name,
            mime="application/json",
            width="stretch",
        )
        st.caption(f"Đã lưu: `transcripts/{Path(st.session_state.transcript_path).name}`")


def main() -> None:
    st.set_page_config(page_title="Research Agent · NhomDHQ", page_icon="🔎")
    load_streamlit_secrets()
    state = st.session_state

    settings = render_sidebar()
    # Compare by value: Streamlit re-runs this file on every interaction, which redefines
    # the Settings class, so `==` between old and new instances would always be False.
    if "settings" not in state or state.pop("restart", False):
        start_conversation(settings)
    elif asdict(settings) != asdict(state.settings):
        start_conversation(settings)
        st.toast("Đã đổi cài đặt, bắt đầu cuộc trò chuyện mới.")

    st.title("🔎 Research Agent")
    st.caption(
        f"Provider `{settings.provider}` · model `{state.transcript['model']}` · "
        f"artifact `{state.artifact_version}`"
    )
    st.markdown(
        "Tìm tin trên web, tweet theo tài khoản hoặc chủ đề, đọc một URL, tìm paper arXiv, "
        "tra cứu policy công ty và tổng hợp thành bản tin. Agent sẽ hỏi lại khi thiếu thông tin "
        "và xin xác nhận trước khi gửi Telegram."
    )

    # chat_input is always pinned to the bottom, so reading it first is safe.
    prompt = st.chat_input("Hỏi agent...") or state.pop("pending_prompt", None)

    if not state.messages and not prompt:
        st.markdown("**Thử nhanh:**")
        cols = st.columns(2)
        for index, sample in enumerate(SAMPLE_PROMPTS):
            cols[index % 2].button(
                sample,
                key=f"sample_{index}",
                width="stretch",
                on_click=lambda text=sample: state.update(pending_prompt=text),
            )

    for message in state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.markdown(message["content"])
            else:
                render_assistant(message)

    if prompt:
        state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Agent đang chọn tool và chạy..."):
                turn = run_turn(prompt)
            message = {
                "role": "assistant",
                "content": turn.get("assistant_text"),
                "status": turn.get("status"),
                "error": turn.get("error"),
                "rounds": turn.get("rounds", []),
            }
            render_assistant(message)
        state.messages.append(message)

    render_download()


main()
