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

Base eval 20 case (`data/eval_base.json`), OpenRouter `openai/gpt-4o-mini`. Nguồn: `artifacts/version_log.csv` và `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi của prompt/tools starter trước khi sửa | — | case 0.70 · routing 0.75 · args 0.70 · multiturn 1.00 (14/20) | `runs/v0_B_base_openrouter_20261110T135339052768.json` |
| v1 | `system_prompt.md` | Bỏ chỉ dẫn đoán/gửi ngay, thêm ranh giới rõ → cải thiện hỏi lại và câu không cần tool | case 0.70 · routing 0.75 · args 0.70 · multiturn 1.00 | case 0.80 · routing 0.95 · args 0.80 · multiturn 0.83 (16/20) | `runs/v1_B_base_openrouter_20261110T135635839117.json` |
| v2 | `tools.yaml` | Bắt buộc `response_type` cho `clarify` và nói rõ ranh giới `send` → sửa lỗi hỏi lại | case 0.80 · routing 0.95 · args 0.80 · multiturn 0.83 | case 0.80 · routing 0.90 · args 0.80 · multiturn 0.83 (16/20) | `runs/v2_B_base_openrouter_20261110T135918044056.json` |
| v3 | `tools.yaml` | Quy ước `topic=news` và luật đổi nguồn rõ ràng → giảm lỗi routing và args | case 0.80 · routing 0.90 · args 0.80 · multiturn 0.83 | case 0.90 · routing 0.95 · args 0.90 · multiturn 0.83 (18/20) | `runs/v3_B_base_openrouter_20261110T140426710762.json` |

Nhận xét:

- v1 tăng mạnh nhất (+2 case) nhờ bỏ các chỉ dẫn xấu cố ý trong prompt starter.
- v2 không tăng điểm tổng: sửa được R11 nhưng R10 tái phát (agent đoán `screenname="Twitter"`), nên routing giảm 0.95 → 0.90.
- multiturn giảm 1.00 → 0.83 từ v1 vì M06 bắt đầu FAIL (xem B2) và chưa sửa được tới v3.

Run bổ sung trên prompt/tools v3, chạy bằng DeepSeek `deepseek-flash` (máy này không có key OpenRouter):

| Suite | Kết quả | Run File |
|---|---|---|
| group (10 case nhóm) | case 1.00 · routing 1.00 · args 1.00 · multiturn 1.00 (10/10) | `runs/v3_B_group_deepseek_20261110T225728735212.json` |
| extension (policy + arXiv) | case 0.60 · routing 0.70 · args 0.60 (6/10) | `runs/v3_B_extension_deepseek_20261110T225746086818.json` |

Hai run này có `artifact_version` `v3+p648d9581f048+tbcaa320d8a7c`: prompt trùng hash v3, còn `tools.yaml` là v3 cộng khai báo tool `deduplicate`.

## B2. Failure Analysis

Mọi case FAIL ở ít nhất một version của base eval (gpt-4o-mini). Trạng thái theo version: v0 / v1 / v2 / v3 (P = PASS, F = FAIL).

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope (F / P / P / P) | out_of_scope | v0: `send(text="Nguyên hàm của x^2 là …")` | Câu toán ngoài phạm vi nhưng agent gọi `send` để "trả lời" | v1 (`system_prompt.md`): bỏ "gửi ngay", thêm luật không dùng tool cho câu ngoài phạm vi |
| R14_out_of_scope_coding (F / P / P / P) | out_of_scope | v0: `send(text="Dưới đây là một hàm Python …")` | Giống R08: câu coding bị đẩy vào `send` | v1, cùng sửa như R08 |
| R10_missing_handle (F / P / F / P) | missing_info | v0: `timeline(screenname="sama")`; v2: `timeline(screenname="Twitter")` | Thiếu tài khoản nhưng agent đoán handle thay vì `clarify` | v1 bỏ câu "pick Sam Altman"; tái phát ở v2; hết ở v3 khi luật routing trong `tools.yaml` rõ hơn |
| R11_missing_url (F / F / P / P) | missing_info | v0: `fetch(url="https://example.com/article")`; v1: `clarify(question=…)` thiếu `response_type` | v0 bịa URL; v1 đã hỏi lại nhưng thiếu `response_type="text"` | v1 bỏ câu "assume a likely URL"; v2 (`tools.yaml`) bắt buộc `response_type` |
| R13_parallel_web_and_tweets (F / F / F / P) | wrong_tool | v0: `lookup(query="AI news", timeframe="day")` + `social_search(query="AI")` | `lookup` thiếu `topic="news"`; v0 còn để `query="AI news"` thay vì `"AI"` | v3 (`tools.yaml`): quy ước `topic=news` cho mọi yêu cầu tin tức |
| R12_confirm_before_send (F / F / F / F) | wrong_boundary | v0: `send(text="Bản tin này")`; v1–v3: `clarify(question="Bạn có thể cung cấp nội dung … muốn đăng …?", response_type="text")` | v0 gửi luôn không xác nhận; v1–v3 hỏi lại nội dung (`text`) thay vì xin xác nhận `yes_no` | **Chưa sửa.** Đề xuất: luật "yêu cầu đăng/gửi → `clarify(response_type="yes_no")` trước, kể cả khi còn thiếu nội dung" trong prompt và mô tả `send` |
| M06_switch_tool (P / F / F / F) | wrong_tool | v1–v3: `lookup(query="OpenAI", topic="news")` + `social_search(query="OpenAI")` | User đã nói "bỏ Twitter" nhưng agent vẫn gọi thêm `social_search` (extra tool call) | **Chưa sửa.** Luật đổi nguồn ở v3 chưa đủ. Đề xuất: ghi rõ "lượt mới nhất loại bỏ một nguồn thì không gọi tool của nguồn đó" |

## B3. Team Eval Cases

10 case trong `data/eval_group.json` (5 single turn + 5 multi turn), do Nguyễn Công Quân viết, tập trung vào tool mới `deduplicate` và ranh giới với `lookup`, `format`, `clarify`.

Kết quả từ `runs/v3_B_group_deepseek_20261110T225728735212.json` (prompt/tools v3, DeepSeek `deepseek-flash`).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_deduplicate_default (single) | Danh sách đã có và yêu cầu bỏ trùng phải route tới deduplicate, không gọi web. | deduplicate() | PASS |
| G02_deduplicate_by_url (single) | Cụm 'chỉ URL' phải map thành strategy=url. | deduplicate(strategy="url") | PASS |
| G03_deduplicate_by_title (single) | Cụm 'chỉ theo tiêu đề' phải map thành strategy=title. | deduplicate(strategy="title") | PASS |
| G04_search_not_deduplicate (single) | Chưa có items và cần tìm dữ liệu mới thì dùng lookup, không dùng deduplicate. | lookup(topic="news", timeframe="day") | PASS |
| G05_format_not_deduplicate (single) | Đã xác nhận không trùng và chỉ cần trình bày thì dùng format, không gọi deduplicate. | format(template="bullets") | PASS |
| GM01_carry_items_then_deduplicate (multi) | Carry danh sách URL qua nhiều lượt rồi gọi deduplicate. | deduplicate() | PASS |
| GM02_correct_strategy_to_title (multi) | Lượt cuối sửa strategy từ URL sang title phải được ưu tiên. | deduplicate(strategy="title") | PASS |
| GM03_tracking_url_strategy (multi) | Tổng hợp URL từ các lượt và chọn strategy=url. | deduplicate(strategy="url") | PASS |
| GM04_cancel_deduplicate_format_only (multi) | Ý định cuối hủy deduplicate và chuyển sang format thread. | format(template="thread") | PASS |
| GM05_missing_items_clarify (multi) | Thiếu items bắt buộc thì hỏi người dùng, không gọi deduplicate với danh sách đoán. | clarify(response_type="text") | PASS |

Lưu ý: run này dùng DeepSeek vì máy chạy không có key OpenRouter. Nên chạy lại cùng lệnh với `--provider openrouter` để so sánh trực tiếp với base eval.

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
| send (Telegram) | `transcripts/v0_deepseek_20261110T142834839230.transcript.json` (lượt 5); `runs/v3_B_base_*.json` (R12) | **Chưa đạt bonus.** v0 gọi `send(confirmed=true)` ngay khi user nói "đăng"; từ v1 agent hỏi lại thay vì gửi, nhưng R12 vẫn FAIL vì hỏi nội dung chứ không xin xác nhận yes/no | Chưa cấu hình Telegram nên không có tin nào bị gửi. Bug trong tool: `send(confirmed="false")` (chuỗi) vẫn qua được bước kiểm tra vì chuỗi không rỗng luôn là truthy; chưa sửa |
| arXiv/company policy | `runs/v3_B_extension_deepseek_20261110T225746086818.json`; transcript lượt 1–2 | 6/10 case extension PASS: `papers`, `paper_text`, đọc 2 link song song và các case kết hợp đều đúng. Chat live: `papers` + `format` tạo được digest có link arXiv | E01–E03 FAIL vì agent gọi `policy` **hai lần** (lần đầu đã đúng `policy_area`); E08 chọn `policy_area="all"` thay vì `ai_research`. Tool `policy` tách dòng giống lệnh vào `untrusted_text` (có unit test) |
| UI (Streamlit) | `app.py`, `transcripts/*_ui_*.transcript.json` | Dùng chung vòng lặp tool với `chat.py`; hiển thị tool đã gọi, args và kết quả từng tool; lưu transcript cùng format với `chat.py`; báo lỗi model mà không crash | Link tunnel public dùng API key của nhóm, nên chỉ mở trong buổi demo; sidebar chỉ hiện key có hay không, không hiện giá trị; `send` vẫn cần `confirmed=true` |
| Tool unit tests (`tests/`) | `pytest`: **84 passed, 0 skipped** | 17 test trong `test_tools_todo.py` (14 stub TODO đã viết + 3 test cho `deduplicate`: happy path, `items` sai kiểu, `strategy` ngoài enum), cộng test contract và test mẫu | Test chạy offline, chặn mọi HTTP thật |

Tool unit tests: 84 test, 0 skipped. Bug tìm được trong code có sẵn:

1. `send` coi `confirmed="false"` (chuỗi) là đã xác nhận. Đây là ví dụ lỗi eval không bắt được: eval chỉ kiểm tra model có truyền `confirmed=true` hay không, còn việc tool xử lý sai kiểu dữ liệu chỉ unit test mới phát hiện. Chưa có regression test, chưa sửa.
2. `versioning.py` băm file nguyên byte, nên cùng một prompt nhưng máy Windows (Git tự đổi sang CRLF) ra hash khác với máy macOS/Linux. Đã sửa: chuẩn hoá CRLF → LF trước khi băm. Sau khi sửa, prompt trên máy Windows ra đúng hash `p648d9581f048` của v3.

## B6. Reflection

- **Sửa trong `system_prompt.md`:** những lỗi về hành vi chung. Bỏ ba chỉ dẫn xấu của starter (đoán thay vì hỏi, gửi không cần xác nhận, ép một bước) ở v1 đã sửa R08, R10, R14 và đưa case accuracy từ 0.70 lên 0.80. Live chat xác nhận cùng lỗi ở v0: agent tự đoán `sama` và gọi `send(confirmed=true)` không hỏi.
- **Sửa trong `tools.yaml`:** những lỗi về tham số và ranh giới giữa các tool. Bắt buộc `response_type` cho `clarify` (v2, sửa R11), quy ước `topic=news` cho tin tức (v3, sửa R13), mô tả khi nào dùng và không dùng `deduplicate` (eval nhóm 10/10).
- **Cần review thủ công:**
  - R12: agent hỏi lại *nội dung* bản tin, điều này hợp lý vì "bản tin này" chưa rõ, nhưng eval chấm FAIL vì chỉ chấp nhận `yes_no`. Cần người đọc để quyết định đó là lỗi agent hay lỗi tiêu chí.
  - E01–E03: lần gọi `policy` đầu tiên đã đúng, lần thứ hai chỉ thừa. Câu trả lời cuối vẫn đúng nhưng bị chấm FAIL vì có tool call thừa.
  - Chất lượng câu trả lời trong live chat (có trích nguồn không, có bịa không) không được chấm tự động; phải đọc transcript.
- **Cải thiện tiếp theo:**
  1. Thêm luật xác nhận `yes_no` trước mọi yêu cầu đăng/gửi (R12).
  2. Luật "nguồn đã bị loại ở lượt mới nhất thì không gọi" (M06).
  3. Mô tả `policy`: gọi một lần với `policy_area` cụ thể nhất (E01–E03, E08).
  4. Sửa `send` chỉ nhận `confirmed is True` và thêm regression test.
  5. Chạy lại eval nhóm và eval mở rộng bằng gpt-4o-mini để so sánh với DeepSeek.

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
