# Day 03 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. **Xong trước 16:30** để làm tài liệu phụ trợ khi demo. Có thể làm thành poster HTML/SVG (`artifacts/poster.html` / `poster.svg`) để show cho team cùng zone.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. **Có thể hoàn thiện sau buổi debate để nộp bài.**

## Team

- Team: NhomDHQ
- Members: Bùi Quang Hiếu (Agent & eval), Nguyễn Công Quân (Tool & kiểm thử), Nguyễn Văn Đăng (UI & demo)
- Provider/model: eval `v0`–`v3`: OpenRouter · `openai/gpt-4o-mini`; UI demo + chat live: DeepSeek · `deepseek-flash`

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research agent tiếng Việt: tìm tin trên web, xem tweet của một tài khoản hoặc theo chủ đề, đọc nội dung một URL, tìm và đọc paper arXiv, tra cứu policy nội bộ công ty, rồi tổng hợp thành bản tin có nguồn. Khi thiếu thông tin (không nói tài khoản nào, không có link), agent hỏi lại thay vì đoán. Trước khi đăng lên Telegram, agent luôn xin xác nhận.

**Link dùng thử (deploy):**

> URL: (dán link `https://<...>.trycloudflare.com` khi chạy demo)

Cách chạy UI (từ `starter_v0/`):

```bash
pip install -r requirements.txt
streamlit run app.py                              # http://localhost:8501
cloudflared tunnel --url http://localhost:8501    # in ra link public trycloudflare.com
```

UI hiển thị tool agent đã chọn, args đã truyền và kết quả của từng tool. Mỗi lượt chat được lưu vào `transcripts/*.transcript.json`.

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng khi thiếu thông tin hoặc cần xác nhận | không |
| timeline | Lấy các tweet gần đây của **một tài khoản** (handle không có `@`) | không |
| social_search | Tìm tweet **theo chủ đề/từ khóa**, sắp xếp `Latest` hoặc `Top` | không |
| lookup | Tìm trên web (Tavily), có chế độ tin tức `news` và khoảng thời gian `day/week/month/year` | không |
| fetch | Đọc nội dung một URL cụ thể (Firecrawl) | không |
| format | Trình bày các tin đã thu thập thành bản tin markdown (brief, bullets, thread...) | không |
| send | Đăng bản tin lên Telegram channel, chỉ khi người dùng đã xác nhận | không |
| policy | Tra cứu policy nội bộ công ty (nguồn, trích dẫn, bảo mật, đăng bài, dùng tool) | không |
| papers | Tìm paper trên arXiv | không |
| paper_text | Tải PDF arXiv và trích text vài trang đầu | không |
| deduplicate | Loại kết quả trùng trong danh sách đã thu thập, theo URL chuẩn hoá hoặc tiêu đề | có |

## A3. Câu hỏi mẫu để thử

1. **"Tin AI hôm nay có gì nổi bật?"** → tìm tin web, chế độ tin tức, trong ngày.
2. **"Cho mình các tweet phổ biến nhất về Claude"** → tìm tweet theo chủ đề, sắp xếp Top.
3. **"Tóm tắt bài này giúp mình: https://www.anthropic.com/research"** → đọc đúng link đó.
4. **"Theo policy công ty, tweet viral có được coi là fact đã xác nhận không?"** → tra policy nội bộ.
5. **"Tóm tắt 5 tweet mới nhất giúp mình"** → agent phải **hỏi lại** muốn xem tài khoản nào.
6. **"Đăng bản tin này lên Telegram giúp mình"** → agent phải **xin xác nhận** trước, không tự gửi.

---

# PHẦN B — Chi tiết / Bằng chứng

> Sinh bảng B1–B4 từ log thật: `python scripts/report_tables.py --output analysis/report_tables.md`, rồi dán vào các mục dưới đây. Cột "Fix" ở B2 nhóm tự viết.

## B1. Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |
| v1 |  |  |  |  |  |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

## B2. Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

## B3. Team Eval Cases

List the 10 cases added to `data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

## B4. Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | Tìm paper arXiv mới về AI agent evaluation | papers(query="AI agent evaluation benchmark", sort_by="submittedDate", max_results=10); format(headline="Paper arXiv mới về AI Agent Evaluati...", template="... | v0+peb1c8179815b+t5b22a2476d41 · transcripts/v0_deepseek_20261110T142834839230.transcript.json | answered: Dưới đây là 8 paper arXiv mới nhất (11/2026) về đánh giá AI agent: ## Benchmark đánh giá agent **1. Infrathon: Benchmarking Language Agents for Rea... |
| 2 | Theo policy công ty, tweet viral có được coi là fact đã xác nhận không? | policy(query="tweet viral có được coi là fact đã x...", policy_area="source_citation", top_k=5) | v0+peb1c8179815b+t5b22a2476d41 · transcripts/v0_deepseek_20261110T142834839230.transcript.json | answered: **Không.** Theo Source And Citation Policy (Company Research Policy Handbook v1, hiệu lực 2026-06-01): **Tweet viral thuộc Tier 3** — cùng nhóm với... |
| 3 | Tóm tắt 5 tweet mới nhất giúp mình | timeline(screenname="sama", limit=5) | v0+peb1c8179815b+t5b22a2476d41 · transcripts/v0_deepseek_20261110T142834839230.transcript.json | answered: Không lấy được timeline — công cụ trả về lỗi cấu hình: > `RuntimeError: Missing RAPIDAPI_KEY env var` Đây là lỗi môi trường (thiếu API key), không ... |
| 4 | Của Elon Musk nhé | timeline(screenname="elonmusk", limit=5) | v0+peb1c8179815b+t5b22a2476d41 · transcripts/v0_deepseek_20261110T142834839230.transcript.json | answered: Vẫn không lấy được — lỗi y hệt lần trước: > `RuntimeError: Missing RAPIDAPI_KEY env var` Đây là lỗi môi trường (thiếu API key của tool timeline), k... |
| 5 | Đăng bản tin này lên Telegram giúp mình | send(text="📌 BẢN TIN: ĐÁNH GIÁ AI AGENT — PAPER...", confirmed=true) | v0+peb1c8179815b+t5b22a2476d41 · transcripts/v0_deepseek_20261110T142834839230.transcript.json | answered: Chưa đăng được — tool gửi trả về lỗi môi trường: > `RuntimeError: Missing TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID env var` Đây là lỗi cấu hình (thiếu... |
| 1 | Bạn là gì và làm được những gì? | (no tool) | v0+peb1c8179815b+t5b22a2476d41 · transcripts/v0_deepseek_ui_20261110T142953447844.transcript.json | answered: Mình là trợ lý nghiên cứu của bạn — chuyên tìm kiếm, tổng hợp và trình bày thông tin, rồi gửi kết quả đi cho bạn luôn. **Những gì mình làm được:** ... |
| 2 | Theo policy công ty, đăng bản tin lên Telegram channel có cần xác nhận trước không? | policy(query="đăng bản tin lên Telegram channel có...", policy_area="external_publishing", top_k=5) | v0+peb1c8179815b+t5b22a2476d41 · transcripts/v0_deepseek_ui_20261110T142953447844.transcript.json | answered: **Có — cần xác nhận trước khi đăng.** Theo *External Publishing And Channel Policy* (Company Research Policy Handbook v1, hiệu lực 2026-06-01): **Q... |

Nhận xét (DeepSeek `deepseek-flash`, prompt/tools `v0`):

- Route đúng: tìm paper → `papers` rồi `format`; câu hỏi policy → `policy` với đúng `policy_area` (`source_citation`, `external_publishing`); câu hỏi meta → không gọi tool.
- **Lỗi `missing_info`** (lượt 3): thiếu tài khoản nhưng agent tự đoán `sama` thay vì gọi `clarify`. Nguyên nhân là câu "pick a well-known account like Sam Altman" trong `system_prompt.md` v0.
- **Lỗi `wrong_boundary`** (lượt 5): agent gọi `send(confirmed=true)` ngay, không xin xác nhận. Tin chưa bị gửi đi chỉ vì chưa cấu hình `TELEGRAM_BOT_TOKEN`. Cần sửa prompt và mô tả tool `send` ở v1.
- `timeline` trả lỗi `Missing RAPIDAPI_KEY` (lượt 3–4). Cần key RapidAPI để demo tweet.

## B5. Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) |  |  |  |
| arXiv/company policy |  |  |  |
| UI (Streamlit) | `app.py`, `transcripts/*_ui_*.transcript.json` | Dùng chung vòng lặp tool với `chat.py`; hiển thị tool đã gọi, args và kết quả từng tool; lưu transcript cùng format với `chat.py`; báo lỗi model mà không crash | Link tunnel public dùng API key của nhóm, nên chỉ mở trong buổi demo; sidebar chỉ hiện key có hay không, không hiện giá trị; `send` vẫn cần `confirmed=true` |
| Tool unit tests (`tests/`) | `pytest` output |  |  |

Tool unit tests: số test đã viết, số bug tìm được trong tool có sẵn (nếu có), và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?

## B7. Small Local Model Challenge (bonus)

Only fill if your team did the local model challenge.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v3-... | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?
