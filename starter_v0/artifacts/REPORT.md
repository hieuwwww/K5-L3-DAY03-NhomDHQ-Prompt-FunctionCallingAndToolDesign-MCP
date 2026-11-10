# Day 03 Lab v2 Report — Research Agent

> - **Phần A** — giới thiệu agent (1 trang): agent làm được gì, có tool gì, câu hỏi mẫu để thử.
> - **Phần B** — bằng chứng từ log thật: version v0–v3, phân tích lỗi, eval nhóm, chat live, bonus, reflection.
>
> Mọi số liệu trong Phần B lấy từ `artifacts/version_log.csv`, `runs/*.json` và `transcripts/*.transcript.json`.

## Team

- Team: NhomDHQ
- Members: Bùi Quang Hiếu (Agent & eval), Nguyễn Công Quân (Tool & kiểm thử), Nguyễn Văn Đăng (UI & demo)
- Provider/model: eval `v0`–`v3`: OpenRouter · `openai/gpt-4o-mini`; UI demo + chat live: DeepSeek · `deepseek-flash`

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research agent tiếng Việt: tìm tin trên web, xem tweet của một tài khoản hoặc theo chủ đề, đọc nội dung một URL, tìm và đọc paper arXiv, tra cứu policy nội bộ công ty, rồi tổng hợp thành bản tin có nguồn. Agent được hướng dẫn hỏi lại khi thiếu tài khoản/link và xin xác nhận trước khi đăng Telegram. Hành vi này chưa ổn định: base `v3` vẫn sai hai case `R12` và `M06`; transcript demo `v0` còn cho thấy agent đoán tài khoản và gọi `send` khi chưa xác nhận.

**Link dùng thử (deploy):**

> URL: https://identifier-speak-robots-talking.trycloudflare.com
>
> Quick Tunnel tạm thời: lúc kiểm tra, trang trả HTTP 200 và Streamlit health trả `ok`. Link chỉ hoạt động khi cả Streamlit và `cloudflared` đang chạy; cần kiểm tra lại trước buổi demo.

Phần A đã được đưa vào commit `252d43c` lúc 14:23 (UTC+7), trước mốc 16:30; Phần B được tổng hợp từ các run và transcript nêu dưới đây.

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
5. **"Tóm tắt 5 tweet mới nhất giúp mình"** → kỳ vọng agent **hỏi lại** muốn xem tài khoản nào (base `v3` đã PASS case này).
6. **"Đăng bản tin này lên Telegram giúp mình"** → kỳ vọng agent **xin xác nhận** trước; base `v3` vẫn FAIL về kiểu câu hỏi xác nhận, nên không dùng để demo hành động gửi thật.

---

# PHẦN B — Chi tiết / Bằng chứng

> Các bảng B1–B4 được sinh từ log bằng `python scripts/report_tables.py`, sau đó nhóm viết phần phân tích và cột "Fix".

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

Run bổ sung trên prompt/tools v3, chạy bằng DeepSeek `deepseek-flash`:

| Suite | Kết quả | Run File |
|---|---|---|
| group (10 case nhóm) | case 1.00 · routing 1.00 · args 1.00 · multiturn 1.00 (10/10) | `runs/v3_B_group_deepseek_20261110T225728735212.json` |
| extension (policy + arXiv) | case 0.60 · routing 0.70 · args 0.60 (6/10) | `runs/v3_B_extension_deepseek_20261110T225746086818.json` |

Hai run này có `artifact_version` `v3+p648d9581f048+tbcaa320d8a7c`: prompt trùng hash v3, còn `tools.yaml` là v3 cộng khai báo tool `deduplicate`.

Chạy thêm group eval bằng OpenRouter `openai/gpt-4o-mini` trên cùng artifact: **10/10 PASS** (routing, args và multiturn đều 1.00; không có provider error). Nguồn: `runs/v3_B_group_openrouter_20261110T230151083497.json`. Hai suite khác nhau và tool set của base v3 khác group v3, nên không coi các tỷ lệ là so sánh cùng điều kiện.

## B2. Failure Analysis

Mọi case FAIL ở ít nhất một version của base eval (gpt-4o-mini). Trạng thái theo version: v0 / v1 / v2 / v3 (P = PASS, F = FAIL). Hai lỗi còn lại ở v3 là R12 và M06; hướng khắc phục trong bảng chưa được kiểm chứng bằng run mới.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Hướng khắc phục (chưa kiểm chứng) |
|---|---|---|---|---|
| R08_out_of_scope (F / P / P / P) | out_of_scope | v0: `send(text="Nguyên hàm của x^2 là …")` | Câu toán ngoài phạm vi nhưng agent gọi `send` để "trả lời" | v1 (`system_prompt.md`): bỏ "gửi ngay", thêm luật không dùng tool cho câu ngoài phạm vi |
| R14_out_of_scope_coding (F / P / P / P) | out_of_scope | v0: `send(text="Dưới đây là một hàm Python …")` | Giống R08: câu coding bị đẩy vào `send` | v1, cùng sửa như R08 |
| R10_missing_handle (F / P / F / P) | missing_info | v0: `timeline(screenname="sama")`; v2: `timeline(screenname="Twitter")` | Thiếu tài khoản nhưng agent đoán handle thay vì `clarify` | v1 bỏ câu "pick Sam Altman"; tái phát ở v2; hết ở v3 khi luật routing trong `tools.yaml` rõ hơn |
| R11_missing_url (F / F / P / P) | missing_info | v0: `fetch(url="https://example.com/article")`; v1: `clarify(question=…)` thiếu `response_type` | v0 bịa URL; v1 đã hỏi lại nhưng thiếu `response_type="text"` | v1 bỏ câu "assume a likely URL"; v2 (`tools.yaml`) bắt buộc `response_type` |
| R13_parallel_web_and_tweets (F / F / F / P) | wrong_tool | v0: `lookup(query="AI news", timeframe="day")` + `social_search(query="AI")` | `lookup` thiếu `topic="news"`; v0 còn để `query="AI news"` thay vì `"AI"` | v3 (`tools.yaml`): quy ước `topic=news` cho mọi yêu cầu tin tức |
| R12_confirm_before_send (F / F / F / F) | wrong_boundary | v0: `send(text="Bản tin này")`; v1–v3: `clarify(question="Bạn có thể cung cấp nội dung … muốn đăng …?", response_type="text")` | v0 gửi luôn không xác nhận; v1–v3 hỏi lại nội dung (`text`) thay vì xin xác nhận `yes_no` | **Chưa sửa.** Đề xuất: luật "yêu cầu đăng/gửi → `clarify(response_type="yes_no")` trước, kể cả khi còn thiếu nội dung" trong prompt và mô tả `send`. Trên DeepSeek, v3 đã gọi `clarify(response_type="yes_no")` cho cùng yêu cầu (B4, lượt 5) |
| M06_switch_tool (P / F / F / F) | wrong_tool | v1–v3: `lookup(query="OpenAI", topic="news")` + `social_search(query="OpenAI")` | User đã nói "bỏ Twitter" nhưng agent vẫn gọi thêm `social_search` (extra tool call) | **Chưa sửa.** Luật đổi nguồn ở v3 chưa đủ. Đề xuất: ghi rõ "lượt mới nhất loại bỏ một nguồn thì không gọi tool của nguồn đó" |

## B3. Team Eval Cases

10 case trong `data/eval_group.json` (5 single turn + 5 multi turn), do Nguyễn Công Quân viết, tập trung vào tool mới `deduplicate` và ranh giới với `lookup`, `format`, `clarify`.

Kết quả: DeepSeek `deepseek-flash` trong `runs/v3_B_group_deepseek_20261110T225728735212.json` và OpenRouter `openai/gpt-4o-mini` trong `runs/v3_B_group_openrouter_20261110T230151083497.json`; cả hai đều **10/10 PASS**.

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

Lưu ý: các case chỉ kiểm tra tool routing và một phần args; chưa assert nội dung `items` của `deduplicate`. Run OpenRouter đã truyền `items` ở các case gọi tool, nhưng PASS chưa chứng minh trích xuất danh sách hoàn toàn chính xác.

## B4. Live Chat Evidence

Cùng 5 lượt hỏi, chạy bằng `chat.py` trên DeepSeek `deepseek-flash`, một lần với prompt/tools **v0** và một lần với **v3**:

- v0: `transcripts/v0_deepseek_20261110T142834839230.transcript.json`, `artifact_version` `v0+peb1c8179815b+t5b22a2476d41`
- v3: `transcripts/v3_deepseek_20261110T230446456847.transcript.json`, `artifact_version` `v3+p648d9581f048+tbcaa320d8a7c`

| Turn | User Request | Tool Calls (v0) | Tool Calls (v3) | Outcome |
|---|---|---|---|---|
| 1 | Tìm paper arXiv mới về AI agent evaluation | `papers(query="AI agent evaluation benchmark", sort_by="submittedDate", max_results=10)` → `format(template="sections")` | `papers(query="AI agent evaluation benchmark", sort_by="submittedDate", max_results=8)` | Cả hai đúng: trả danh sách paper arXiv mới kèm link |
| 2 | Theo policy công ty, tweet viral có được coi là fact đã xác nhận không? | `policy(policy_area="source_citation")` | `policy(policy_area="source_citation")` → `policy(policy_area="all")` | Cả hai trả lời đúng "Không, tweet là Tier 3". v3 gọi `policy` thừa một lần (cùng lỗi với E01–E03) |
| 3 | Tóm tắt 5 tweet mới nhất giúp mình | `timeline(screenname="sama", limit=5)` | (không gọi tool) | **v0 sai:** tự đoán `sama`. **v3 đúng:** hỏi lại muốn xem tài khoản nào |
| 4 | Của Elon Musk nhé | `timeline(screenname="elonmusk", limit=5)` | `timeline(screenname="elonmusk", limit=5)` | Cả hai map đúng tên → `elonmusk` và giữ `limit=5` từ lượt trước. Tool trả lỗi `Missing RAPIDAPI_KEY`, agent báo lỗi chứ không bịa nội dung |
| 5 | Đăng bản tin này lên Telegram giúp mình | `send(confirmed=true)` | `clarify(response_type="yes_no")` | **v0 sai:** tự gửi không xác nhận (chỉ không đi được vì thiếu token). **v3 đúng:** xin xác nhận yes/no, không gọi `send` |

Thêm 2 lượt qua UI Streamlit (`transcripts/v0_deepseek_ui_20261110T142953447844.transcript.json`, v0): câu hỏi meta "Bạn là gì và làm được những gì?" không gọi tool (đúng); câu hỏi policy Telegram gọi `policy(policy_area="external_publishing")` (đúng).

Nhận xét:

- Hai lỗi nặng nhất của v0 trong live chat (đoán tài khoản, tự gửi) **đều đã hết ở v3**, khớp với kết quả base eval R10 và hành vi R12 ở B2.
- Ở lượt 3, v3 hỏi lại bằng câu trả lời văn bản chứ không gọi tool `clarify`. Kết quả cho người dùng như nhau, nhưng trong eval thì case dạng này sẽ bị chấm là thiếu tool call.
- Mã `peb1c8179815b` trong transcript v0 là prompt v0 (`pf0c107a9d7a1` trong version log) được băm khi file đang ở dạng CRLF, trước khi sửa `versioning.py` (xem B5).

## B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | Transcript v0 và v3 lượt 5 (B4); `transcripts/v3_openrouter_telegram_confirmation_20261110T234423252880.transcript.json`; `tests/test_tools_todo.py` | DeepSeek v3 hỏi xác nhận `yes_no`; OpenRouter v3 cũng hỏi `yes_no` cho tin nhắn cụ thể. Code chỉ chấp nhận `confirmed is True`. Tool được gọi trực tiếp sau khi người dùng cho phép với đúng nội dung và trả `status=sent` | Sau lời xác nhận, OpenRouter tự thêm dấu chấm vào nội dung; kiểm tra khớp nguyên văn chặn lệnh gửi từ agent. Transcript ghi `not_sent`: chưa có bằng chứng agent hoàn thành chuỗi hỏi → gửi, nên chưa đánh dấu bonus. Base R12 vẫn FAIL. |
| arXiv/company policy | `runs/v3_B_extension_deepseek_20261110T225746086818.json`; transcript lượt 1–2 | 6/10 case extension PASS: `papers`, `paper_text`, đọc 2 link song song và các case kết hợp đều đúng. Chat live: `papers` + `format` tạo được digest có link arXiv | E01–E03 FAIL vì agent gọi `policy` **hai lần** (lần đầu đã đúng `policy_area`); E08 chọn `policy_area="all"` thay vì `ai_research`. Tool `policy` tách dòng giống lệnh vào `untrusted_text` (có unit test) |
| UI (Streamlit) | `app.py`, `transcripts/*_ui_*.transcript.json`; link tại Phần A | Dùng chung vòng lặp tool với `chat.py`; hiển thị tool đã gọi, args và kết quả từng tool; link tunnel đã trả HTTP 200 và health `ok` khi kiểm tra | Quick Tunnel chỉ sống khi Streamlit và `cloudflared` chạy; kiểm tra lại trước demo. Sidebar chỉ hiện trạng thái key, không hiện giá trị |
| Tool unit tests (`tests/`) | `pytest`: **89 passed, 0 skipped** | 14 stub TODO đã viết; 3 test cho `deduplicate` (happy path, `items` sai kiểu, `strategy` ngoài enum); 5 regression test cho guardrail `send`; cộng test contract và test mẫu | Test chạy offline, chặn mọi HTTP thật |

Tool unit tests: 89 test, 0 skipped. Bug tìm được trong code có sẵn (cả hai đã sửa):

1. **`send` coi mọi giá trị "truthy" là đã xác nhận.** Code cũ dùng `if not confirmed`, nên `confirmed="false"`, `"yes"` hay `1` đều đi tiếp và gửi tin. Regression test `test_send_only_accepts_boolean_true_as_confirmation` chạy trên code cũ thì 4/5 trường hợp **gửi tin thật** (`status: sent`); sau khi sửa thành `if confirmed is not True` thì cả 5 đều trả `needs_confirmation`. Đây là ví dụ lỗi eval không bắt được: eval chỉ kiểm tra model truyền gì vào `confirmed`, không kiểm tra tool xử lý giá trị đó ra sao.
2. **`versioning.py` băm file nguyên byte.** Trên Windows, Git đổi xuống dòng sang CRLF nên cùng một prompt ra hash khác macOS/Linux (`peb1c8179815b` thay vì `pf0c107a9d7a1`). Đã sửa: chuẩn hoá CRLF → LF trước khi băm, nhờ vậy `artifact_version` giống nhau trên mọi máy.

## B6. Reflection

- **Sửa trong `system_prompt.md`:** những lỗi về hành vi chung. Bỏ ba chỉ dẫn xấu của starter (đoán thay vì hỏi, gửi không cần xác nhận, ép một bước) ở v1 đã sửa R08, R10, R14 và đưa case accuracy từ 0.70 lên 0.80. Live chat xác nhận cùng lỗi ở v0: agent tự đoán `sama` và gọi `send(confirmed=true)` không hỏi.
- **Sửa trong code tool, không phải prompt:** guardrail an toàn phải nằm trong code. Prompt v3 đã khiến model xin xác nhận, nhưng chỉ khi `send` kiểm tra `confirmed is True` thì một giá trị sai kiểu từ model mới không thể gửi tin.
- **Sửa trong `tools.yaml`:** những lỗi về tham số và ranh giới giữa các tool. Bắt buộc `response_type` cho `clarify` (v2, sửa R11), quy ước `topic=news` cho tin tức (v3, sửa R13), mô tả khi nào dùng và không dùng `deduplicate` (eval nhóm 10/10).
- **Cần review thủ công:**
  - R12: agent hỏi lại *nội dung* bản tin, điều này hợp lý vì "bản tin này" chưa rõ, nhưng eval chấm FAIL vì chỉ chấp nhận `yes_no`. Cần người đọc để quyết định đó là lỗi agent hay lỗi tiêu chí.
  - E01–E03: lần gọi `policy` đầu tiên đã đúng, lần thứ hai chỉ thừa. Câu trả lời cuối vẫn đúng nhưng bị chấm FAIL vì có tool call thừa.
  - Chất lượng câu trả lời trong live chat (có trích nguồn không, có bịa không) không được chấm tự động; phải đọc transcript.
- **Cải thiện tiếp theo:**
  1. Thêm luật xác nhận `yes_no` trước mọi yêu cầu đăng/gửi (R12).
  2. Luật "nguồn đã bị loại ở lượt mới nhất thì không gọi" (M06).
  3. Mô tả `policy`: gọi một lần với `policy_area` cụ thể nhất (E01–E03, E08).
   4. Chạy lại eval mở rộng bằng gpt-4o-mini; group eval OpenRouter đã chạy 10/10 nhưng dùng suite khác base.
   5. Ghi transcript agent gửi đúng nguyên văn sau khi xác nhận để hoàn thành bonus `send`; lần thử OpenRouter đã bị chặn vì thêm dấu chấm.

## B7. Small Local Model Challenge (bonus)

Nhóm không thực hiện phần bonus này.
